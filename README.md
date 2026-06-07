# Meituan AutoSolver Agent

美团 AI Hackathon 04 AutoSolver 赛题最终交付仓库。仓库只保留 release 级材料：最终 `solver.py`、本地合法性 smoke test，以及精简技术文档。

本项目面向带随机完成概率的配送分配问题，将平台输入抽象为候选边集合，在任务互斥、骑手互斥、bundle exact-match 和运行时限制下，最小化期望配送成本。

## Result

- 历史最优 release 平台平均分：`710.8817`
- 平台有效性：`10 / 10` cases valid
- 未分配任务：`0`
- 提交文件：`solver.py`
- 文件大小：`89,958` bytes
- 依赖：Python standard library only
- 接口：`solve(input_text: str) -> list`

本题目标分数为期望成本与未分配惩罚的综合指标，分数越低越好。

## Problem Formulation

输入候选边：

```text
task_id_list    courier_id    total_score    willingness
```

输出为若干 `(task_id_list, [courier_id, ...])`。任一输出边必须在当前输入中 exact 存在；任务与骑手均不可重复使用。

工程上该问题不是单纯 assignment，而是 set packing、bundle selection、probabilistic redundancy 和 runtime-bounded local optimization 的混合问题。不同 case profile 的结构差异明显：骑手稀缺 case 偏覆盖组合，低意愿 case 偏冗余分配，大规模 case 偏稳定全覆盖。

## Method

最终 solver 采用 profile-aware portfolio，而非单一启发式：

- `Profile Router`：按任务数、骑手数、稀缺度、willingness 分布和 bundle 形态切分策略空间。
- `Assignment Core`：组合 greedy、min-cost single matching、pair matching、beam search 与 local repair。
- `Feedback Replay`：只在当前输入完整支持时重放已验证结构，避免历史结构产生非法 edge。
- `Scarce-Courier Search`：使用 pair cover、subset repair、exact LNS、pair reshuffle 和 bounded random LNS。
- `Redundancy Optimizer`：在低意愿场景中用 expected-cost evaluator 控制多骑手冗余收益与成本。
- `Runtime Guardrails`：单文件、无第三方依赖、有限候选宽度、显式时间检查、全路径合法性验证。

离线阶段由 Agent 生成与筛选多类 solver 变体；release 阶段只保留通过平台反馈、运行时约束和 strict validity 检验的策略组合。

## Validation

提交前检查项：

- `python3 -m py_compile solver.py`
- `python3 tools/local_validate.py`
- strict edge membership
- duplicate task / courier check
- profile-level runtime review

`tools/local_validate.py` 仅用于本地 smoke validation；平台结果以正式评测记录为准。

## Repository

```text
.
├── solver.py
├── tools/
│   └── local_validate.py
└── docs/
    ├── solution_design.md
    ├── experiment_log_summary.md
    └── final_submission_record.md
```

- `solver.py`：最终 release solver。
- `tools/local_validate.py`：本地接口与合法性 smoke test。
- `docs/solution_design.md`：建模、策略调度与工程护栏。
- `docs/experiment_log_summary.md`：实验路线与取舍。
- `docs/final_submission_record.md`：hash、平台摘要与回滚方案。

## Run

```bash
python3 -m py_compile solver.py
python3 tools/local_validate.py
```

## Scope

本仓库不包含账号凭证、平台交互 dump、隐藏评测行、完整实验工作区、生成缓存或无关探索代码。
