# Final Submission Record

## Solver

- Final solver file: `solver.py`
- Release version: `v318d_t30_threshold520`
- SHA256: `622e891989ac87486dc8c9151506b23da5e116a83d5e56fdf26c032d332c9acb`
- File size: `89,958` bytes
- `py_compile`: PASS
- Dependencies: Python standard library only

## 平台摘要

最终 release 记录时间：2026-06-08。

| Metric | Value |
| --- | ---: |
| Average score | `710.8817` |
| Valid cases | `10 / 10` |
| Unassigned tasks | `0` |
| Slowest case runtime | `9,420 ms` |

Per-case score summary:

| Case | Score | Assigned | Unassigned | Runtime |
| --- | ---: | ---: | ---: | ---: |
| `high_noise_seed601.txt` | `500.3380` | `30` | `0` | `9,160 ms` |
| `large_seed301.txt` | `659.0928` | `40` | `0` | `5,008 ms` |
| `large_seed302.txt` | `629.6188` | `40` | `0` | `3,526 ms` |
| `low_willingness_seed501.txt` | `1801.9723` | `30` | `0` | `9,290 ms` |
| `medium_seed201.txt` | `487.3950` | `30` | `0` | `9,300 ms` |
| `medium_seed202.txt` | `526.2980` | `30` | `0` | `9,287 ms` |
| `medium_seed203.txt` | `503.5249` | `30` | `0` | `9,299 ms` |
| `scarce_couriers_seed401.txt` | `1526.6982` | `40` | `0` | `9,420 ms` |
| `small_seed100.txt` | `315.2485` | `15` | `0` | `448 ms` |
| `tiny_seed42.txt` | `158.6303` | `6` | `0` | `98 ms` |

## Release 风险

- solver 含 bounded search 和 time checks；更慢的 Python runtime 可能减少 local repair 执行量。
- feedback seed replay 受当前输入支持校验约束；profile 若发生明显变化，相关 fast path 会自动让位给搜索。
- low-willingness case 仍然是最难 profile，因为本地 proxy 改进有时会偏离平台期望成本。

## Rollback Plan

1. 本 release 以 `solver.py` 和上述 SHA256 为准。
2. 未来如出现合法性或分数回退，先恢复该 hash，再跑 compile 与本地 validation。
3. 新策略只在通过 strict output validation 和 per-profile runtime review 后再进入 release。
