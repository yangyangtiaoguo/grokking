"""
Autoregressive LARGECOUNTER (minimal reproduction), faithful to Zhao ACL 2026.

Vocab {0,1,#} (ids 0,1,2). Sequence: bin(N) # bin(N+1), BIG-ENDIAN (MSB first).
Model is a causal decoder-only Transformer; loss only on the bin(N+1) target
tokens (the tokens AFTER the '#'). This is next-token prediction, and crucially
big-endian makes carry NON-LOCAL: to emit the MSB of N+1 the model must know
whether a carry propagates all the way up from the LSB (which appears LATER in
the sequence). That non-locality is what the paper says creates grokking
(little-endian would collapse it to a trivial 2-state Mealy machine).

Grokking setup (Omnigrok/Power/Zhao): high weight decay + train on a subset of N
values, eval on held-out N values. Generalization = learning the ripple-carry
algorithm rather than memorizing the training N's.
"""
import numpy as np
import torch
import torch.nn as nn

PAD, SEP = 2, 2  # '#' token id = 2 ; we also use 2 as pad (masked out in loss)
VOCAB = 3


def bits_be(x, n):
    """big-endian n-bit representation of x, shape (n,)."""
    return np.array([(x >> (n - 1 - i)) & 1 for i in range(n)], dtype=np.int64)


def make_sequences(xs, n):
    """For each N in xs build token seq [bin(N) big-endian, #, bin(N+1) big-endian].
    Returns input_ids (B, 2n+1) and a loss mask that is 1 only on the n target bits.
    Target for position t is token at t+1 (standard causal shift)."""
    B = len(xs)
    L = 2 * n + 1
    seq = np.zeros((B, L), dtype=np.int64)
    for i, N in enumerate(xs):
        a = bits_be(N, n)
        b = bits_be((N + 1) % (2 ** n), n)
        seq[i, :n] = a
        seq[i, n] = SEP
        seq[i, n + 1:] = b
    # loss mask on the positions whose NEXT token is a target bit:
    # target bits occupy indices [n+1, 2n]; they are predicted from indices [n, 2n-1]
    mask = np.zeros((B, L), dtype=np.float32)
    mask[:, n:2 * n] = 1.0
    return seq, mask


def split_train_eval(n, frac, seed):
    rng = np.random.default_rng(seed)
    allN = np.arange(2 ** n, dtype=np.int64)
    perm = rng.permutation(allN)
    ntr = int(frac * len(allN))
    return np.sort(perm[:ntr]), np.sort(perm[ntr:])


def zipf_split_train(n, alpha, frac, seed):
    """Skewed training set: sample N ~ (N+1)^(-alpha) without replacement to size frac."""
    rng = np.random.default_rng(seed)
    allN = np.arange(2 ** n, dtype=np.int64)
    w = (allN + 1.0) ** (-alpha); w /= w.sum()
    ntr = int(frac * len(allN))
    tr = rng.choice(allN, size=ntr, replace=False, p=w)
    mask = np.ones(len(allN), dtype=bool); mask[tr] = False
    return np.sort(tr), np.sort(allN[mask])


def to_tensors(xs, n, device):
    seq, mask = make_sequences(xs, n)
    return (torch.from_numpy(seq).to(device),
            torch.from_numpy(mask).to(device))


def zipf_batch_sampler(n, alpha, batch, seed):
    """Frequency-skew sampler (the d0 mechanism's protocol): draw minibatch
    indices WITH replacement from all 2^n states, weighted by (x+1)^(-alpha).
    alpha=0 -> uniform. p1v2 showed that subset-selection (zipf_split_train)
    leaves the carry composition of the train set ~unchanged in alpha, so the
    d0 mechanism does NOT exist under subset selection — only under frequency
    weighting. Yields indices into the full 0..2^n-1 training pool."""
    rng = np.random.default_rng(seed)
    w = (np.arange(2 ** n, dtype=np.float64) + 1.0) ** (-alpha)
    w /= w.sum()
    while True:
        yield rng.choice(2 ** n, size=batch, replace=True, p=w)


# ----------------------------- model -----------------------------

class RoPE(nn.Module):
    def __init__(self, dim, base=10000.0):
        super().__init__()
        inv = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv, persistent=False)

    def _cs(self, T, device, dtype):
        t = torch.arange(T, device=device).float()
        f = torch.outer(t, self.inv_freq)
        emb = torch.cat([f, f], -1)
        return emb.cos().to(dtype), emb.sin().to(dtype)

    @staticmethod
    def _rot(x):
        x1, x2 = x.chunk(2, -1)
        return torch.cat([-x2, x1], -1)

    def forward(self, q, k):
        T = q.shape[-2]
        cos, sin = self._cs(T, q.device, q.dtype)
        cos, sin = cos[None, None], sin[None, None]
        return q * cos + self._rot(q) * sin, k * cos + self._rot(k) * sin


class Attn(nn.Module):
    def __init__(self, d, h):
        super().__init__()
        self.h, self.dh = h, d // h
        self.qkv = nn.Linear(d, 3 * d, bias=False)
        self.proj = nn.Linear(d, d, bias=False)
        self.rope = RoPE(self.dh)

    def forward(self, x):
        B, T, D = x.shape
        q, k, v = self.qkv(x).chunk(3, -1)
        q = q.view(B, T, self.h, self.dh).transpose(1, 2)
        k = k.view(B, T, self.h, self.dh).transpose(1, 2)
        v = v.view(B, T, self.h, self.dh).transpose(1, 2)
        q, k = self.rope(q, k)
        o = torch.nn.functional.scaled_dot_product_attention(q, k, v, is_causal=True)
        return self.proj(o.transpose(1, 2).reshape(B, T, D))


class Block(nn.Module):
    def __init__(self, d, h, m=4):
        super().__init__()
        self.ln1 = nn.LayerNorm(d); self.attn = Attn(d, h)
        self.ln2 = nn.LayerNorm(d)
        self.mlp = nn.Sequential(nn.Linear(d, m * d), nn.ReLU(), nn.Linear(m * d, d))

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        return x + self.mlp(self.ln2(x))


class ARCounter(nn.Module):
    def __init__(self, n, d=64, heads=4, layers=2, vocab=VOCAB):
        super().__init__()
        self.n = n
        self.embed = nn.Embedding(vocab, d)
        self.blocks = nn.ModuleList([Block(d, heads) for _ in range(layers)])
        self.ln_f = nn.LayerNorm(d)
        self.head = nn.Linear(d, vocab)

    def forward(self, ids):
        x = self.embed(ids)
        for b in self.blocks:
            x = b(x)
        return self.head(self.ln_f(x))  # (B,L,vocab)


def param_l2(model):
    return float(sum((p.detach() ** 2).sum().item() for p in model.parameters()) ** 0.5)


def scale_init(model, s):
    if s == 1.0:
        return model
    with torch.no_grad():
        for m in model.modules():
            if isinstance(m, nn.Linear):
                m.weight.mul_(s)
                if m.bias is not None:
                    m.bias.mul_(s)
    return model


@torch.no_grad()
def seq_accuracy(model, ids, mask, batch=4096):
    """Whole-number accuracy: all n target bits of N+1 correct."""
    model.eval()
    ok = tot = 0
    for i in range(0, ids.shape[0], batch):
        x = ids[i:i+batch]; m = mask[i:i+batch]
        logits = model(x)
        pred = logits.argmax(-1)          # (B,L)
        tgt = x.roll(-1, dims=1)          # next-token targets
        correct = ((pred == tgt) | (m == 0)).all(dim=1)  # all masked positions right
        ok += correct.sum().item(); tot += x.shape[0]
    return ok / tot
