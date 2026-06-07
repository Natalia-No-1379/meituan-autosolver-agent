# Experiment Log Summary

## Research Route

项目从 score-first greedy 和简单 bundle 策略起步，先建立稳定合法 baseline。这类版本可解释、风险低，但没有充分利用 willingness、bundle 结构和 case profile，分数空间有限。

随后进入 profile routing 阶段：按任务数、骑手数、稀缺度和 willingness 分布拆分 case。这个阶段解决了“一套启发式跨 profile 互相伤害”的问题，让 tiny、medium、large、scarce-courier、low-willingness 可以分别调度。

第三阶段是 portfolio search：min-cost single matching、pair cover、bundle-first heuristic、local repair、bounded LNS 等策略并行进入候选池。最有效的方向不是单个更大的搜索，而是“便宜合法覆盖 + 针对性修复”的组合。

最后阶段把验证过的优质结构沉淀为 guarded feedback seeds。它们只有在当前输入完整支持时才会 replay；如果支持不完整，solver 会回退到 profile search，避免输出非法候选。

## What Worked

- profile-specific routing 明显减少跨 case 回退；
- exact-edge validation 避免历史字符串在新输入中变成非法输出；
- scarce-courier pair cover 与 repair 是稀缺骑手 case 全覆盖的关键；
- multi-courier redundancy 在部分 low-willingness row 上能降低期望失败成本；
- bounded local search 在平台时间限制内提供了稳定收益。

## What Was Rejected

- 无界 wrapper：运行时间和递归行为不可控；
- aggressive low-willingness expansion：本地 proxy 好看，但平台收益不稳定；
- 无 profile gating 的 broad global search：容易在已有 fast path 的 case 上浪费时间；
- 不做 current-input support check 的 hardcoded output strings。

## Release Decision

最终 release 选择最高置信度组合：stable feedback replay、profile thresholds、scarce-courier repair 和 bounded runtime search。它不是最大的研发产物，而是能保留关键技术决策、保持交付干净、并复现历史最优平台结果的最小 solver。
