# Solution Design

## 建模

AutoSolver 输入是一组候选边。每条边由 `task_id_list`、`courier_id`、`total_score` 和 `willingness` 描述，表示某个骑手可以执行一个任务集合。任务集合可能是单任务，也可能是 bundle。

solver 需要选择若干候选边，允许在当前输入支持时为同一个任务集合配置多个骑手，同时满足任务不重复、骑手不重复、候选边必须 exact 存在等硬约束。

内部目标近似为期望成本：

```text
expected row cost = P(success) * expected score + P(failure) * unassigned penalty
```

因此这是 set packing、bipartite assignment、bundle selection 和 probability-aware redundancy 的混合问题。不同 profile 的最优结构差异很大，所以最终 solver 使用 profile router，而不是一个全局公式。

## Runtime Flow

1. 解析 TSV 输入，建立 exact edge map、score map、task universe 和 courier universe。
2. 提取 profile 特征：任务数、骑手数、稀缺比例、willingness 分布、singleton、pair 和 bundle。
3. 运行多策略 candidate generator。
4. 用统一 expected-cost evaluator 给候选解打分。
5. 只保留通过合法性校验的当前最优解。
6. 通过 `solve(input_text)` 返回平台要求的 list 结构。

每个候选解都必须通过硬校验：不重复任务、不重复骑手、不输出当前输入中不存在的候选边。

## Strategy Portfolio

最终 release 保留的策略组合包括：

- score / density greedy baseline，用于快速得到合法覆盖；
- shortest augmenting path min-cost flow，用于单任务最小成本匹配；
- guarded feedback seed replay，用于稳定 profile 的快速返回；
- multi-courier augmentation，用于 willingness 较低时降低失败概率；
- local search，在不破坏合法性的前提下移动骑手、降低期望成本；
- pair-density、pair-saving、pair-beam matching，用于 scarce-courier coverage；
- scarce subset repair、exact LNS、pair reshuffle、random LNS，用于困难 bundle case。

调度顺序是先跑便宜且稳定的 baseline，再根据剩余时间和 profile 选择是否进入更深的 repair。

## Profile Decisions

- Tiny / small：规模小，优先轻量策略，避免多余搜索。
- Medium / high-noise：依赖 feedback seeds、matching 和 multi-courier local repair。
- Large：优先稳定全覆盖与 fast path，避免宽搜索拖慢运行。
- Scarce-courier：以 pair cover 和 LNS-style repair 为核心，因为每个骑手通常要覆盖多个任务。
- Low-willingness：谨慎增加冗余骑手；冗余能降低失败概率，但也可能抬高 expected score。

## 工程护栏

- 单文件 release solver；
- 不依赖第三方库；
- beam width、candidate 数量和 LNS 深度都有上界；
- 深搜索路径显式检查 `time.perf_counter()`；
- candidate 成为 best 前必须通过 exact-edge validity；
- 本地 smoke validator 覆盖 import、接口形状和基础 strict legality。

离线研发阶段可以生成很多候选 solver，但 release 只保留经平台分数、合法性、运行时和可审阅性共同筛选后的策略组合。
