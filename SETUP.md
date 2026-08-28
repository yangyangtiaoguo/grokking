# 实验环境 SETUP

**锁定日期**：2026-08-21。后续所有实验都用本环境。

## 硬件
- GPU：**RTX 5080 16GB**（Blackwell, **sm_120**, capability (12,0)）
- 驱动 580.173.02，运行时 CUDA 13.0，nvcc 12.8
- 机器 sophgo-System-Product-Name，Ubuntu 24.04，kernel 7.0，磁盘 /（3.7T，~1.3T 空闲）

## 关键约束
- sm_120 **必须**用 **PyTorch cu128** wheel。cu121/cu124 会报 `no kernel image available for execution on the device`。
- 已验证：`torch 2.11.0+cu128`，`torch.cuda.get_device_capability(0)==(12,0)`，GPU matmul 实测通过。

## 隔离环境
- 工具：`uv 0.10.2`（`/home/nsc/.local/bin/uv`）
- venv：`/home/nsc/coding/grokking_research/.venv`（Python 3.12.12）
- 已装：`torch==2.11.0+cu128`, `triton==3.6.0`, `numpy`, `matplotlib`

## 复现安装
```bash
cd /home/nsc/coding/grokking_research
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python torch --index-url https://download.pytorch.org/whl/cu128
uv pip install --python .venv/bin/python numpy matplotlib
```

## 运行约定
- 跑脚本：`.venv/bin/python experiments/<name>.py`（不必 activate）
- 或 `source .venv/bin/activate` 后直接 `python`
- 结果存 `results/`，图存 `figures/`，脚本存 `experiments/`

## 已完成
- `experiments/p0_combinatorics.py` — P0 组合学预检（零 GPU）。GO。见 `选题现状说明.md` 第 7 节。
- `experiments/p0_plot.py` — P0 可视化 → `figures/p0_carry_stats.png`

## 待做（先导协议顺序）
- P1 训练到记忆态测 Δℓ(α)（需 LARGECOUNTER 任务 + 2 层 Transformer）
- P2 双阱插值 / P3 自由能序关系 / P4 相图 2×2 角点
