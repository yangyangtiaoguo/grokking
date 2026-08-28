"""
Shared task + model for the grokking phase-diagram experiments.

LARGECOUNTER: given an n-bit integer x (LSB-first bit sequence), predict the
bits of increment(x) = (x+1) mod 2^n. Per-position binary classification.

Ripple-carry ground truth: out_i = x_i XOR carry_i, where carry_0 = 1 and
carry_{i+1} = x_i AND carry_i  (i.e. carry propagates through trailing ones).
So the number of flipped bits = trailing-ones count + 1 = c(x)+1  (the carry
chain), directly linking difficulty to the carry statistics from P0.

magnitude-Zipf sampling: P_alpha(x) ∝ (x+1)^(-alpha) over x in [0, 2^n).
"""
import numpy as np
import torch
import torch.nn as nn


# ----------------------------- data -----------------------------

def int_to_bits_lsb(x, n):
    """x: (B,) int64 -> (B, n) float bits, LSB first."""
    bits = ((x[:, None] >> np.arange(n)[None, :]) & 1).astype(np.float32)
    return bits


def increment_bits(x, n):
    """Ground-truth increment(x) mod 2^n as LSB-first bits."""
    y = (x + 1) % (2 ** n)
    return int_to_bits_lsb(y, n)


def carry_chain_len(x):
    """c(x) = trailing ones. Vectorized."""
    x = x.astype(np.int64)
    c = np.zeros_like(x)
    active = np.ones_like(x, dtype=bool)
    bit = 0
    while active.any() and bit <= 64:
        mask = ((x >> bit) & 1) == 1
        c[active & mask] += 1
        active = active & mask
        bit += 1
    return c


def zipf_sample(n, alpha, size, rng):
    """Sample x ~ P_alpha(x) ∝ (x+1)^(-alpha) over [0, 2^n)."""
    x = np.arange(2 ** n, dtype=np.int64)
    w = (x + 1.0) ** (-alpha)
    w /= w.sum()
    return rng.choice(x, size=size, p=w)


def make_split(n, alpha, n_train, seed=0, full_eval_cap=1 << 16):
    """Build a fixed train set (Zipf-alpha, with repeats collapsed to unique)
    and an eval set = all 2^n states (or a uniform cap)."""
    rng = np.random.default_rng(seed)
    train_x = np.unique(zipf_sample(n, alpha, n_train, rng))
    N = 2 ** n
    if N <= full_eval_cap:
        eval_x = np.arange(N, dtype=np.int64)
    else:
        eval_x = rng.choice(N, size=full_eval_cap, replace=False).astype(np.int64)
    return train_x, eval_x


def to_tensors(x, n, device):
    xb = torch.from_numpy(int_to_bits_lsb(x, n)).to(device)
    yb = torch.from_numpy(increment_bits(x, n)).to(device)
    return xb, yb


# ----------------------------- model -----------------------------

class RoPE(nn.Module):
    """Rotary positional embedding applied to q,k of shape (B,H,T,Dh)."""
    def __init__(self, dim, base=10000.0):
        super().__init__()
        inv = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv, persistent=False)

    def _cos_sin(self, T, device, dtype):
        t = torch.arange(T, device=device).float()
        freqs = torch.outer(t, self.inv_freq)  # (T, Dh/2)
        emb = torch.cat([freqs, freqs], dim=-1)  # (T, Dh)
        return emb.cos().to(dtype), emb.sin().to(dtype)

    @staticmethod
    def _rotate_half(x):
        x1, x2 = x.chunk(2, dim=-1)
        return torch.cat([-x2, x1], dim=-1)

    def forward(self, q, k):
        T = q.shape[-2]
        cos, sin = self._cos_sin(T, q.device, q.dtype)
        cos, sin = cos[None, None], sin[None, None]
        q = q * cos + self._rotate_half(q) * sin
        k = k * cos + self._rotate_half(k) * sin
        return q, k


class Attn(nn.Module):
    def __init__(self, d, heads):
        super().__init__()
        self.h, self.dh = heads, d // heads
        self.qkv = nn.Linear(d, 3 * d, bias=False)
        self.proj = nn.Linear(d, d, bias=False)
        self.rope = RoPE(self.dh)

    def forward(self, x):
        B, T, D = x.shape
        q, k, v = self.qkv(x).chunk(3, dim=-1)
        q = q.view(B, T, self.h, self.dh).transpose(1, 2)
        k = k.view(B, T, self.h, self.dh).transpose(1, 2)
        v = v.view(B, T, self.h, self.dh).transpose(1, 2)
        q, k = self.rope(q, k)
        # full (non-causal) attention; counting needs to look at lower bits
        o = torch.nn.functional.scaled_dot_product_attention(q, k, v)
        o = o.transpose(1, 2).reshape(B, T, D)
        return self.proj(o)


class Block(nn.Module):
    def __init__(self, d, heads, mlp_mult=4):
        super().__init__()
        self.ln1 = nn.LayerNorm(d)
        self.attn = Attn(d, heads)
        self.ln2 = nn.LayerNorm(d)
        self.mlp = nn.Sequential(
            nn.Linear(d, mlp_mult * d), nn.ReLU(), nn.Linear(mlp_mult * d, d)
        )

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x


class Counter(nn.Module):
    """2-layer encoder-only Transformer. Input: n bits (as tokens), output: n bits."""
    def __init__(self, n, d=64, heads=4, layers=2):
        super().__init__()
        self.n = n
        self.embed = nn.Linear(1, d)          # each bit -> d
        self.blocks = nn.ModuleList([Block(d, heads) for _ in range(layers)])
        self.ln_f = nn.LayerNorm(d)
        self.head = nn.Linear(d, 1)           # per-position logit

    def forward(self, bits):                  # bits: (B, n)
        x = self.embed(bits[..., None])       # (B, n, d)
        for blk in self.blocks:
            x = blk(x)
        x = self.ln_f(x)
        return self.head(x).squeeze(-1)       # (B, n) logits


def param_l2(model):
    return float(sum((p.detach() ** 2).sum().item() for p in model.parameters()) ** 0.5)


def scale_init(model, scale):
    """Multiply all Linear weights by `scale` to move init onto a higher-norm
    shell — the Omnigrok lever for inducing grokking (large init + weight decay)."""
    if scale == 1.0:
        return model
    with torch.no_grad():
        for m in model.modules():
            if isinstance(m, nn.Linear):
                m.weight.mul_(scale)
                if m.bias is not None:
                    m.bias.mul_(scale)
    return model


@torch.no_grad()
def bit_and_seq_acc(model, xb, yb, batch=8192):
    """Return (per-bit acc, whole-sequence acc)."""
    model.eval()
    nb = ns = tot = totseq = 0
    for i in range(0, xb.shape[0], batch):
        logit = model(xb[i:i+batch])
        pred = (logit > 0).float()
        y = yb[i:i+batch]
        nb += (pred == y).sum().item()
        tot += y.numel()
        seq_ok = (pred == y).all(dim=1)
        ns += seq_ok.sum().item()
        totseq += y.shape[0]
    return nb / tot, ns / totseq
