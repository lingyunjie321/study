# 面试私有知识库_最终版

## 00 文档元信息与检索规则

---
chunk_id: KB-META-001
title: 文档用途与切块规则
category: facts
tags: [文档元信息, RAG, 面试辅助 Agent, 切块, 检索规则]
aliases: [知识库怎么用, 面试检索规则, chunk schema]
trigger_questions:
  - 这份知识库是给谁用的？
  - 面试辅助 Agent 应该怎么检索这份文档？
short_answer: |
  这份文档是给面试辅助 Agent 使用的私有知识卡片库，不是论文、源码讲解或长篇项目总结。每个 chunk 都围绕一个明确问题组织，检索到后可以直接生成口语化回答。建议按独立分隔线切块入向量库，优先用 `title`、`tags`、`aliases`、`trigger_questions` 做关键词和语义检索，用 `pitfalls` 约束模型不要夸大。
deep_answer: |
  文档服务的场景是：面试官提出一个自然语言问题，Agent 快速召回 1 到 3 个相关 chunk，再交给大模型生成候选人口吻的回答。因此每个 chunk 都保留了短回答、深回答、追问方向、坑点和事实状态。

  数字、成果和边界类问题优先检索 `KB-FACT` 和 `KB-FIN`；算法问题优先检索 `KB-RL` 和 `KB-ENT`；工程问题优先检索 `KB-AGENT` 和 `KB-DIST`；压力面问题优先检索 `KB-PRESS`，并强制参考 `pitfalls`。
follow_up_questions:
  - 一个问题召回多个 chunk 时怎么排序？
  - fact_status 有什么用？
follow_up_answer_points:
  - 先选能直接回答问题的 chunk，再补充相邻机制 chunk。
  - `confirmed` 可作为硬事实；`to_verify` 只能谨慎提；`future_direction` 只能说规划。
pitfalls:
  - 不要把这份文档当作源码定位表使用。
  - 不要跳过 `pitfalls` 直接生成夸大回答。
fact_status: confirmed
related_chunks: [KB-IDX-001, KB-FACT-001]
---

---
chunk_id: KB-META-002
title: 统一回答口径
category: facts
tags: [事实口径, 不夸大, 已确认, 待确认, 项目边界]
aliases: [哪些能说, 哪些不能说, 事实状态]
trigger_questions:
  - 面试时哪些事实可以直接说？
  - 哪些项目成果需要谨慎？
short_answer: |
  可以直接说的事实包括：项目主体是 `ae-ARPO/`；金融训练集 3391 行、验证集 508 行；通用推理训练集 10000 行；深度搜索数据 1071 行；金融评估共 1020 题；金融综合结果采用 77.6%。需要谨慎的说法包括 GAIA 61.2% Pass@5、工具调用频率降低约 50%、API 调用降低 15-30% 和完整 ablation 收益，这些只能作为待确认或经验口径。
deep_answer: |
  最终版统一采用金融优化文档和本次数据核对的口径：finance 综合 340 题、FinBench 200 题、8 个领域专项各 60 题，总计 1020 题；金融综合 77.6%，FinBench 高难 45.5%，领域专项平均 73.8%。旧文档摘要里出现过一个较低的冲突旧口径，与后续金融文档和核对口径冲突，最终版不采用。

  AEARPO/ARAEPO 的表达也要稳妥：二者都属于面向 Agent RL 的熵平衡优化系列。AEARPO 更侧重 rollout、工具调用和分支采样效率；ARAEPO 更强调 policy update 阶段的 entropy-aware advantage 和稳定性机制。
follow_up_questions:
  - 如果面试官问旧摘要里的冲突低口径怎么办？
  - 如果面试官要求 GAIA 或工具调用下降结果怎么办？
follow_up_answer_points:
  - 说明旧摘要低口径与后续金融文档冲突，最终统一到 77.6%。
  - GAIA 和工具调用下降数字可以说“文档中有口径，但我会标为待确认，不作为主结果主动宣传”。
pitfalls:
  - 不要混用旧摘要低口径和 77.6%。
  - 不要把待确认数字包装成已验证主结果。
fact_status: confirmed
related_chunks: [KB-FACT-001, KB-FIN-003]
---

## 01 项目开场回答

---
chunk_id: KB-OPEN-001
title: 一句话介绍
category: open
tags: [项目定位, FIN-Agentic RL, AEARPO, ARAEPO, LLM Agent, 强化学习]
aliases: [一句话项目, 项目是什么, 简历项目介绍]
trigger_questions:
  - 用一句话介绍这个项目。
  - 这个项目解决什么问题？
short_answer: |
  我会把这个项目理解为一个面向工具调用 LLM Agent 的强化学习训练项目：基于 verl、Ray、vLLM 和 FSDP，让模型更稳定地进行搜索、Python 计算和多轮推理。核心问题是 Agent 轨迹里工具返回、分支采样和长序列会引入高不确定性，所以项目围绕 AEARPO/ARAEPO 做熵平衡训练、工具调用稳定性和金融经济领域扩展。
deep_answer: |
  普通问答微调更多训练“一次性回答”，而这个项目关注的是 Agent 轨迹：模型可能先推理、调用搜索或 Python 工具、读取结果、再继续推理。这个过程有外部工具噪声、长短轨迹不均、最终答案级 reward 和多轮状态管理问题。

  我在面试中会重点讲四层：算法上使用 GRPO/PPO 风格的 policy optimization 并引入熵信号；工程上接入 ToolAgent、去重、循环检测、重试和监控；系统上通过 Ray、vLLM、FSDP、DataProto 跑分布式训练；领域上构建金融经济 8 子领域数据和三层评估体系。
follow_up_questions:
  - 和普通 RLHF 有什么不同？
  - 为什么工具调用会让训练更难？
follow_up_answer_points:
  - 普通 RLHF 多是单轮回答，Agent RL 是多轮轨迹和工具环境。
  - 工具返回改变上下文状态，reward 多在最终答案上，信用分配更难。
pitfalls:
  - 不要说从零实现了 verl、Ray、vLLM、FSDP、PPO 或 GRPO。
  - 不要把金融实时行情、多轮财务建模说成已完成成果。
fact_status: confirmed
related_chunks: [KB-SCOPE-001, KB-ENT-001, KB-FIN-001]
---

---
chunk_id: KB-OPEN-002
title: 30 秒介绍
category: open
tags: [30秒介绍, elevator pitch, 项目开场, 简历回答]
aliases: [半分钟介绍, 快速介绍项目]
trigger_questions:
  - 30 秒介绍一下你的项目。
  - 简历上 FIN-Agentic RL 是什么？
short_answer: |
  这个项目是做 LLM Agent 强化学习训练的，底层基于 verl，目标是让模型更稳定地完成搜索、Python 计算和多轮推理。我的工作主要围绕 AEARPO/ARAEPO 的熵平衡机制、工具调用稳定性、分布式训练接入和金融经济数据扩展。金融部分构建了 8 个子领域、4239 条 QA 和 1020 题评估体系，统一口径下 Qwen3-14B + AEARPO 的金融综合结果是 77.6%。
deep_answer: |
  30 秒版不要展开太多公式，重点说清“项目类型、难点、方法、产出”。项目类型是 Agent RL，不是普通 SFT；难点是工具调用带来的高熵、长轨迹和最终答案 reward；方法是 SFT 冷启动加 GRPO/RL，再用熵机制和工程稳定性手段控制训练；产出是金融数据、评估和工程闭环。

  如果面试官继续追问结果，可以补充 FinBench 高难 45.5%、8 领域专项平均 73.8%。如果追问 GAIA 或工具调用频率下降，则要说这些数字需要进一步实验报告确认。
follow_up_questions:
  - 你的个人贡献是什么？
  - 金融结果怎么评估？
follow_up_answer_points:
  - 贡献分算法理解与接入、Agent 工程、金融数据、评估体系四层讲。
  - 金融评估分综合、高难和领域专项三层。
pitfalls:
  - 不要主动塞太多未经确认的性能数字。
  - 不要把 4239 条全部说成训练集，训练集是 3391 行。
fact_status: confirmed
related_chunks: [KB-OPEN-003, KB-SCOPE-001, KB-FIN-003]
---

---
chunk_id: KB-OPEN-003
title: 1 分钟介绍
category: open
tags: [1分钟介绍, Agent RL, 熵平衡, 工具调用, 金融大模型]
aliases: [一分钟项目介绍, 背景方法结果]
trigger_questions:
  - 用 1 分钟完整介绍这个项目。
  - 从背景、方法和结果讲一下。
short_answer: |
  这个项目可以理解为一个面向工具调用 Agent 的 RL 训练系统。背景是 Instruct 模型会回答问题，但不一定稳定地多轮搜索、执行 Python 和利用工具结果；直接做 GRPO 时，工具返回后的高熵 token、长轨迹和分支采样会让优化变得不稳定。方法上，项目用 SFT 冷启动加 GRPO/RL 微调，并在 AEARPO/ARAEPO 中引入熵相关机制；工程上做了工具去重、循环检测、指数退避和监控；结果上扩展了金融 8 子领域数据和 1020 题评估，金融综合口径是 77.6%。
deep_answer: |
  我会把训练链路拆成两段：SFT 先让模型学会工具调用格式和多轮交互模式，RL 再优化何时调用工具、调用什么、调用后如何使用结果。因为很多任务只有最终答案分数，所以项目更偏 GRPO 这种基于组内多采样的 outcome reward 优化。

  系统层用 Ray 编排 worker 和 GPU 资源，vLLM 做高吞吐 rollout，FSDP 做大模型训练，DataProto 在模块间传递 tensor 和非 tensor 信息。Agent 层支持搜索和 Python 工具，并通过 call limit、去重、循环检测、重试和状态校验提高训练稳定性。
follow_up_questions:
  - 为什么需要 SFT 冷启动？
  - 为什么用 GRPO 而不是 PPO？
follow_up_answer_points:
  - SFT 降低工具协议探索成本，RL 优化决策质量。
  - GRPO 省 critic 显存，适合最终答案级 reward 和多采样比较。
pitfalls:
  - 不要说所有实验都打开了所有熵机制，具体要看配置。
  - 不要把工具安全说成生产级。
fact_status: confirmed
related_chunks: [KB-RL-002, KB-RL-004, KB-DIST-002]
---

---
chunk_id: KB-OPEN-004
title: 3 分钟介绍
category: open
tags: [3分钟介绍, 项目深挖, 方法论, 工程实现, 结果分析]
aliases: [详细项目介绍, 深度介绍项目]
trigger_questions:
  - 详细介绍一下这个项目。
  - 从问题、方案、工程和结果完整讲一下。
short_answer: |
  3 分钟我会按“问题、方法、工程、领域扩展、结果和反思”讲。问题是工具调用 Agent 的 RL 训练比普通问答难，因为轨迹长、工具返回不确定、reward 多是最终答案级。方法是 SFT 冷启动加 GRPO/RL 微调，并通过 AEARPO/ARAEPO 的熵平衡思路处理高不确定性位置。工程上用 Ray、vLLM、FSDP、DataProto 和 ToolAgent 跑分布式多轮训练。领域上扩展金融经济 8 子领域数据，结果显示计算型任务好于监管概念和高难金融数学任务。
deep_answer: |
  背景上，Agent 任务要求模型在外部环境里行动。比如一个金融估值题，模型可能需要搜索背景、用 Python 计算 WACC 或 NPV，再综合成答案。这个过程里的工具结果会改变上下文，导致 token 熵、序列长度和 reward 信号都不稳定。

  方法上，SFT 解决“会不会按协议调工具”，RL 解决“工具调用策略是否更优”。GRPO 通过同一 prompt 的多条 trajectory 做相对优势估计，减少 critic 负担。熵机制则用于识别和调节高不确定性位置，让训练信号更贴合 Agent 轨迹结构。

  工程和领域上，项目把工具状态机、去重、循环检测、指数退避、显存切换、sequence balancing、checkpoint 转换和金融数据 schema 都串成闭环。结果方面，金融综合 77.6%，FinBench 高难 45.5%，说明基础计算和公式题较好，但复杂估值、Monte Carlo、监管概念仍是短板。
follow_up_questions:
  - 最关键的工程难点是什么？
  - 当前最大短板是什么？
follow_up_answer_points:
  - 工程难点是多轮状态、工具失败、长序列、显存切换和分布式数据一致性。
  - 短板是高难金融推理、概念题评估和完整 ablation 还需补充。
pitfalls:
  - 不要把未来规划写成已实现，比如实时金融搜索、pandas 财务建模、LLM-as-judge。
  - 不要把工程整合包装成理论原创。
fact_status: confirmed
related_chunks: [KB-SCOPE-002, KB-ENT-004, KB-FIN-004]
---

## 02 个人贡献与项目边界

---
chunk_id: KB-SCOPE-001
title: 个人贡献总述
category: scope
tags: [个人贡献, 项目边界, 简历真实性, 二次开发, 工程落地]
aliases: [你做了什么, 哪些是你的工作, 项目贡献]
trigger_questions:
  - 这个项目你具体做了什么？
  - 哪些是框架已有能力，哪些是你的工作？
short_answer: |
  我不会把这个项目说成从零写了完整 RL 框架，底座是 verl、Ray、vLLM、FSDP 和现有大模型训练生态。我的贡献主要是四块：理解并接入 AEARPO/ARAEPO 的熵平衡训练口径；围绕工具调用 Agent 做去重、循环检测、重试、监控和状态校验；构建金融经济 8 子领域数据并适配 Parquet/reward_model schema；设计金融三层评估并整理结果和短板。
deep_answer: |
  面试里要把“框架能力”和“项目增量”分开。框架提供了大模型 RL 的基本训练能力，我的工作是在 Agent 工具调用和金融经济任务里把这套能力落地：让数据能被训练管线读取，让 reward 能对齐 ground truth，让工具调用不因为重复、循环和超时拖垮 rollout，让评估能按领域和难度诊断问题。

  如果面试官问“是不是只是复现”，我会承认有复现和二次开发成分，但强调复现不是终点。真正的工作在于跑通训练、工具、数据、评估和分析闭环，并明确项目哪些结论已经核对、哪些还需要进一步实验。
follow_up_questions:
  - 算法层面你做了什么？
  - 工程层面你做了什么？
follow_up_answer_points:
  - 算法层：GRPO/PPO、熵机制、KL、clip、训练稳定性理解和配置。
  - 工程层：ToolAgent 稳定性、分布式训练参数、checkpoint、评估链路。
pitfalls:
  - 不要说独立发明了 PPO、GRPO、Ray 或 vLLM。
  - 不要把“支持某机制”直接说成“实验证明提升很多”。
fact_status: confirmed
related_chunks: [KB-PRESS-001, KB-FACT-001]
---

---
chunk_id: KB-SCOPE-002
title: 已完成与未来方向
category: scope
tags: [已完成, 未来优化, roadmap, 项目边界, 不夸大]
aliases: [哪些实现了, 哪些是计划, 项目短板]
trigger_questions:
  - 哪些已经实现，哪些只是后续计划？
  - 这个项目未来怎么优化？
short_answer: |
  已完成的是训练框架接入、工具调用 Agent 工程优化、金融经济数据构建、Parquet/JSONL 格式适配和三层评估结果分析。未来方向包括公开金融数据导入、实时行情搜索、pandas 财务建模、多轮金融工具任务、金融专用 reward、LLM-as-judge、中文金融数据和高难金融数学增强。这些未来方向不能包装成已完成成果。
deep_answer: |
  判断已完成工作可以看是否有稳定产物：金融训练和验证 Parquet、finance/finbench/finance_domains 评估 JSONL、工具 Agent 配置、训练脚本和金融优化文档。未来方向则主要是提升真实性、多样性和评估精度，例如从公开金融数据集补真实财报任务，引入 LLM-as-judge 改善概念题评分，加入 Python 工具做复杂金融建模。

  压力面里最稳的说法是：当前版本完成了格式兼容、训练接入和评估闭环；真正生产级金融 Agent 仍需要实时数据、工具安全、细粒度 reward、人工校验和更强的领域数据。
follow_up_questions:
  - 为什么不现在就做实时行情？
  - LLM-as-judge 为什么还没作为主评估？
follow_up_answer_points:
  - 实时行情引入可复现性、成本、权限和时效问题，需要单独设计。
  - LLM-as-judge 有偏差和成本，适合作为概念题补充，不宜未经校准直接作为唯一主指标。
pitfalls:
  - 不要说金融工具链和实时行情已经完成。
  - 不要把公开数据大规模导入说成当前训练主数据来源。
fact_status: confirmed
related_chunks: [KB-FIN-005, KB-FIN-006, KB-PRESS-002]
---

---
chunk_id: KB-SCOPE-003
title: 不展示源码时怎么讲清实现
category: scope
tags: [不展示源码, 实现讲解, 面试表达, 工程抽象]
aliases: [面试官要看代码, 不能展示源码, 怎么解释实现]
trigger_questions:
  - 如果面试官要求看代码但你不展示源码怎么办？
  - 不讲源码行号怎么证明你理解实现？
short_answer: |
  我会用模块边界和数据流讲实现，而不是报源码行号。比如训练链路可以讲成：Hydra 加载配置，Ray 初始化 worker，DataLoader 读取 Parquet，vLLM 生成 trajectory，ToolAgent 管理工具循环，reward manager 根据 ground truth 打分，GRPO 计算 advantage，FSDP 更新 actor，最后保存 checkpoint。这样既能体现实现细节，又不会依赖源码展示。
deep_answer: |
  面试官真正想验证的是你是否理解系统，而不是背文件名。可以用“输入、状态、输出、失败处理”四个维度讲每个模块：ToolAgent 的输入是当前 token 序列和工具配置，状态包括 active indices、call counters、dones、工具调用历史，输出是完整 response 和 mask；失败处理包括 timeout、重试、循环终止和错误结果回填。

  算法部分也类似：不要说“某个函数第几行”，而是讲 GRPO 的 group baseline、熵标准化后的 advantage 重加权、PPO ratio、clip、dual-clip 和 mask。这样回答更适合技术面。
follow_up_questions:
  - 面试官继续追问具体细节怎么办？
  - 如何证明不是只看了文档？
follow_up_answer_points:
  - 用关键状态、张量字段、配置开关和异常场景解释。
  - 能讲出数据 schema、mask、工具失败、显存切换和 checkpoint 限制，说明理解过实现。
pitfalls:
  - 不要硬背行号或路径来制造熟悉感。
  - 不要因为不展示源码就回避实现细节。
fact_status: confirmed
related_chunks: [KB-DIST-005, KB-AGENT-001, KB-PRESS-004]
---

## 03 RL 与大模型训练基础

---
chunk_id: KB-RL-001
title: PPO 核心思想
category: rl
tags: [PPO, policy optimization, ratio, clipping, GAE, Actor-Critic]
aliases: [PPO为什么clip, PPO和GAE, 策略更新]
trigger_questions:
  - PPO 的核心思想是什么？
  - PPO 为什么需要裁剪？
short_answer: |
  PPO 的核心是限制策略更新幅度，避免一次梯度更新把模型策略推得太远。它用新旧策略概率比 `r = pi_new / pi_old`，通过 clipped surrogate objective 把更新约束在 `[1-epsilon, 1+epsilon]` 附近。GAE 是优势估计方法，PPO 是策略更新目标，两者常一起用，但不是同一个概念。
deep_answer: |
  在大模型 RL 中，如果 reward 一高就无限放大某些 token 概率，下一轮采样分布可能漂移，语言质量和工具行为都会变差。PPO 的 clip 相当于给 policy update 加一个软约束，让模型在提升 reward 的同时不突然偏离旧策略。

  PPO 可以搭配 critic 和 GAE，也可以和其他 advantage estimator 组合。项目里更常讲 GRPO，是因为很多工具调用任务只有最终答案级 reward，训练 critic 的收益未必抵消显存和噪声成本。
follow_up_questions:
  - PPO 一定需要 critic 吗？
  - clip ratio 太大或太小会怎样？
follow_up_answer_points:
  - 经典 PPO 常用 Actor-Critic，但 PPO 本身是更新目标。
  - clip 太大容易不稳定，太小学习慢。
pitfalls:
  - 不要把 PPO 和 GAE 混为一谈。
  - 不要把 PPO 说成落后算法，只是本任务更偏 GRPO。
fact_status: confirmed
related_chunks: [KB-RL-002, KB-RL-006]
---

---
chunk_id: KB-RL-002
title: GRPO 为什么适合
category: rl
tags: [GRPO, PPO, critic, outcome reward, group baseline, advantage]
aliases: [为什么不用critic, GRPO优势, group relative]
trigger_questions:
  - GRPO 和 PPO 有什么区别？
  - 为什么这个项目更适合 GRPO？
short_answer: |
  GRPO 不单独训练 critic，而是对同一个 prompt 采样多条 trajectory，用组内 reward 均值和标准差做相对优势：`A_i = (R_i - mean_group) / (std_group + epsilon)`。工具调用、金融问答和数学推理很多时候只有最终答案级分数，GRPO 正好适合 outcome-level reward，同时能省下 critic 显存，把资源留给 rollout、长上下文和 vLLM KV cache。
deep_answer: |
  Agent 任务中，同一个问题可以走不同路径：直接回答、搜索后回答、Python 计算后回答。只要最终 reward 能区分哪条轨迹更好，就可以在组内做相对比较。相比训练 critic 去估计每个中间状态价值，GRPO 的工程复杂度和显存压力更低。

  但 GRPO 也有缺点：如果同组样本全对或全错，reward 方差很小，优势信号会弱；如果任务需要细粒度步骤反馈，critic 或过程 reward 可能更合适。因此回答时要说“更适合本项目”，不要说“永远优于 PPO”。
follow_up_questions:
  - GRPO 不用 critic，信用分配怎么办？
  - group std 为 0 怎么办？
follow_up_answer_points:
  - 信用分配主要靠同组多采样和最终 reward，相对比较轨迹质量。
  - std 过小需要 epsilon、退化保护或增加采样多样性。
pitfalls:
  - 不要说不用 critic 就没有 baseline，GRPO 的 baseline 是组内均值。
  - 不要说 GRPO 完全解决长轨迹信用分配。
fact_status: confirmed
related_chunks: [KB-RL-003, KB-RL-005, KB-PRESS-005]
---

---
chunk_id: KB-RL-003
title: Outcome Reward 的利弊
category: rl
tags: [outcome reward, reward model, rule-based, credit assignment, 最终答案奖励]
aliases: [结果奖励, 最终答案打分, reward局限]
trigger_questions:
  - outcome-level reward 的局限是什么？
  - 为什么金融任务用 rule-based reward？
short_answer: |
  Outcome reward 的优点是简单、可复现，适合数学题、金融计算题和最终答案明确的问题；缺点是信用分配粗，只知道整条轨迹对不对，不知道中间哪一步贡献最大。这个项目主要依赖 ground truth、数值容差、F1 或关键点匹配做自动评分，能支撑训练闭环，但对开放式金融分析和监管概念题仍不够细。
deep_answer: |
  对 NPV、WACC、CAPM、久期这类计算题，最终数值和公式步骤比较明确，rule-based reward 可以给出稳定信号。对监管合规、风险解释、宏观政策分析这类问题，同义表达很多，关键词匹配可能误判，需要 LLM-as-judge 或人工抽样补充。

  因此面试中可以说当前 reward 更适合可验证的结构化推理，未来要加入步骤级评分、单位检查、关键概念覆盖和 judge rubric。不要说当前 reward 已经能完全评价金融专业推理质量。
follow_up_questions:
  - 如何改进信用分配？
  - 为什么不用训练 reward model？
follow_up_answer_points:
  - 引入过程 reward、步骤匹配、工具结果使用检查和 LLM-as-judge。
  - 训练 reward model 需要标注数据和偏差控制，当前先用 rule-based 跑通闭环。
pitfalls:
  - 不要把完整分步答案等同于已经实现步骤级 reward。
  - 不要说 rule-based 评估完全等价人工金融专家。
fact_status: mixed
related_chunks: [KB-FIN-002, KB-FIN-006, KB-PRESS-003]
---

---
chunk_id: KB-RL-004
title: SFT 冷启动
category: rl
tags: [SFT, 冷启动, agentic SFT, 工具调用格式, LoRA, 全参微调]
aliases: [为什么先SFT, 直接RL行不行, 工具协议学习]
trigger_questions:
  - PPO/GRPO 训练为什么需要 SFT 冷启动？
  - SFT 和 RL 分别学什么？
short_answer: |
  SFT 冷启动先教模型“会不会按协议做工具调用”，RL 再优化“什么时候调、调什么、调几次、调完怎么用”。Instruct 模型通常擅长一次性回答，不一定会稳定输出工具标签和多轮交互格式。直接 RL 会把大量预算浪费在摸索工具协议上，收敛慢、失败率高。
deep_answer: |
  项目文档里提到约 54K agentic SFT 数据，作用是让模型学会 system prompt、工具调用标记、工具结果和多轮回复的基本模式。SFT 后模型具备可行动作空间，RL 才能根据 reward 优化策略。

  默认口径是全参数微调配合 FSDP 分片；如果显存不足，可以通过 LoRA 作为工程折中。面试时可以说全参上限更高、LoRA 更省显存，但具体选择要看模型规模、GPU 和实验目标。
follow_up_questions:
  - 没有 SFT 会怎样？
  - LoRA 会不会影响效果？
follow_up_answer_points:
  - 没有 SFT，工具标签、调用时机和多轮格式都不稳定。
  - LoRA 省显存但可能限制容量，全参成本高但表达能力更充分。
pitfalls:
  - 54K 是项目文档口径，若被问数据来源细节，需要进一步核查。
  - 不要说 SFT 已经学到最优工具策略。
fact_status: mixed
related_chunks: [KB-OPEN-003, KB-RL-002, KB-AGENT-001]
---

---
chunk_id: KB-RL-005
title: Advantage、Mask 与归一化
category: rl
tags: [advantage, response_mask, loss_mask, masked whiten, padding, GRPO]
aliases: [优势归一化, mask作用, 工具结果mask]
trigger_questions:
  - 为什么 advantage 要归一化？
  - response_mask 和 loss_mask 有什么作用？
short_answer: |
  Advantage 归一化是为了让不同 prompt 的 reward 尺度可比，避免某些题天然分数高或低导致训练不稳定。Mask 的作用是只在有效的模型生成 token 上计算 loss，排除 padding 和外部工具返回内容。Agent 轨迹里工具结果不是模型动作，如果不 mask 掉，模型会被错误训练成“生成工具结果”。
deep_answer: |
  GRPO 依赖同组样本的 reward 相对差异，因此必须保留 uid 或等价分组信息。Sequence balancing 或 batch reorder 之后，如果分组关系丢了，就会把不同 prompt 的 reward 混在一起。

  长序列 Agent RL 中，mask 比普通问答更关键：每条轨迹长度不同，工具返回长度不同，有些分支提前结束。如果 loss 对 padding、工具结果或无效位置计算，就会污染梯度，并放大训练不稳定。
follow_up_questions:
  - sequence balancing 会影响 GRPO 分组吗？
  - 工具结果 token 要不要训练？
follow_up_answer_points:
  - 只要 uid 和分组元信息保留，重排不会影响分组。
  - 工具结果来自环境，通常不作为 policy action 训练。
pitfalls:
  - 不要说所有 token 都参与 policy gradient。
  - 不要忽略 group size 太小或 reward 方差为 0 的退化问题。
fact_status: confirmed
related_chunks: [KB-DIST-003, KB-DIST-004, KB-ENT-003]
---

---
chunk_id: KB-RL-006
title: KL 与训练稳定性
category: rl
tags: [KL, KL penalty, reference policy, kl_loss, policy drift, reward hacking]
aliases: [KL正则, 策略偏移, in-reward KL]
trigger_questions:
  - KL 在这个项目里有什么作用？
  - in-reward KL 和 kl_loss 有什么区别？
short_answer: |
  KL 用来限制当前策略不要偏离参考策略太远，防止 reward 优化把模型带偏。in-reward KL 是从 token-level reward 中扣掉 `beta * KL`，会影响 advantage；kl_loss 是在 policy loss 中额外加 KL 惩罚，更像优化层面的正则。GRPO 虽然不用 critic，但仍可以用 KL 控制语言质量、格式和工具行为不要漂移。
deep_answer: |
  Agent RL 的 reward 可能只看最终答案是否正确，如果没有约束，模型可能学到奇怪格式、过度调用工具或 reward hacking。KL 相当于把模型拉回参考模型附近，让它在提高任务 reward 的同时保持基本语言能力。

  KL 系数可以固定，也可以自适应。太高会压制学习，太低会导致策略漂移。面试中要区分 KL 和 entropy：entropy 看单个策略分布的不确定性，KL 看两个分布之间的差异。
follow_up_questions:
  - KL 系数怎么调？
  - KL 和熵有什么区别？
follow_up_answer_points:
  - 可根据当前 KL、clipfrac、reward 曲线动态调整。
  - 熵衡量随机性，KL 衡量新旧策略或参考策略偏移。
pitfalls:
  - 不要说 KL 只在 PPO 里有用。
  - 不要把 KL、entropy、temperature 混成一个概念。
fact_status: confirmed
related_chunks: [KB-RL-001, KB-ENT-001]
---

## 04 AEARPO/ARAEPO 熵平衡机制

---
chunk_id: KB-ENT-001
title: 为什么需要熵
category: entropy
tags: [entropy, 高熵 token, 工具返回, 探索, 不确定性, Agent RL]
aliases: [为什么关注熵, 高熵有价值吗, 熵平衡]
trigger_questions:
  - 为什么工具调用 Agent 需要熵机制？
  - 高熵 token 为什么值得关注？
short_answer: |
  熵衡量模型在某个位置有多不确定，公式是 `H = -sum p log p`。工具返回、搜索摘要、Python 输出和分支选择会让模型面对新信息，这些位置往往高熵，也更影响后续决策。熵机制不是奖励高随机性，而是把“不确定且可能关键的位置”纳入采样和训练权重控制。
deep_answer: |
  普通回复里很多 token 是固定模板，模型已经很确定，训练价值有限。Agent 轨迹的关键位置常在工具结果之后：模型要判断结果是否可信、是否继续搜索、如何整合证据。标准 GRPO 如果对所有 token 一视同仁，这些位置的信号可能被长序列中的普通 token 稀释。

  高熵不是高价值的同义词。它只是说明模型分布不确定，可能包含信息增益，也可能只是混乱。因此熵机制必须配合 KL、clip、call limit、去重和循环检测，避免鼓励胡乱探索。
follow_up_questions:
  - 熵越高越好吗？
  - 熵会不会鼓励乱试？
follow_up_answer_points:
  - 不是越高越好，高熵只是需要关注，不等于正确。
  - 通过分支上限、KL、工具限制和失败降级控制探索。
pitfalls:
  - 不要说高熵 token 一定更重要或更正确。
  - 不要把熵机制说成简单调高 temperature。
fact_status: confirmed
related_chunks: [KB-ENT-003, KB-ENT-004, KB-PRESS-006]
---

---
chunk_id: KB-ENT-002
title: AEARPO 与 ARAEPO 命名关系
category: entropy
tags: [AEARPO, ARAEPO, 命名演进, rollout, policy update, 熵平衡]
aliases: [两个名字区别, AEARPO和ARAEPO, 命名混用]
trigger_questions:
  - AEARPO 和 ARAEPO 有什么区别？
  - 为什么仓库里有两个名字？
short_answer: |
  稳妥口径是：AEARPO 和 ARAEPO 都属于面向 Agent RL 的熵平衡优化系列，仓库里存在命名演进。AEARPO 更侧重 rollout、工具调用和分支采样效率；ARAEPO 更强调 policy update 阶段的 entropy-aware advantage 和相关稳定性机制。不要把它们讲成完全无关的两个项目，也不要强行编造一个没有冲突的命名故事。
deep_answer: |
  面试官追问命名时，坦诚比硬解释更好。可以说：项目迭代中出现了 AEARPO/ARAEPO 两套目录和文档口径，我在面试里会统一归纳为 Agent RL 的熵平衡优化系列。

  机制上，rollout 阶段关注如何把采样预算给更有信息增益的轨迹，避免重复工具调用；policy update 阶段关注如何让高不确定性 token 的 advantage 和更新行为更稳定。两者共同服务于工具调用 Agent 的训练效率和稳定性。
follow_up_questions:
  - 三个熵机制分别是什么？
  - 哪些开关一定打开了吗？
follow_up_answer_points:
  - Dynamic Rollout、Entropy-Aware Advantage、熵相关 policy update 稳定机制。
  - 不同脚本可能通过配置开关控制，不能说所有实验都打开。
pitfalls:
  - 不要说每个机制都有完整独立 ablation 收益。
  - 不要把命名差异讲成严密论文术语。
fact_status: confirmed
related_chunks: [KB-ENT-003, KB-ENT-004, KB-ENT-005]
---

---
chunk_id: KB-ENT-003
title: Entropy-Aware Advantage
category: entropy
tags: [Entropy-Aware Advantage, entropy_normalized, advantage, detach, alpha 0.2]
aliases: [熵感知优势, 熵权重0.2, advantage重加权]
trigger_questions:
  - 熵感知 advantage 怎么实现？
  - 熵权重 0.2 怎么解释？
short_answer: |
  可确认的核心机制是：用有效 token 的 entropy 做标准化，再调节 advantage，口径可写成 `A' = A * (1 + alpha * z_H)`，其中 `z_H = (H - mean(H)) / std(H)`，项目常见 `alpha` 为 0.2。`detach()` 表示熵只作为权重调节信号，不让熵标准化本身引入额外梯度路径。
deep_answer: |
  这一步的直觉是：同一条回答里，不是每个 token 对最终 reward 的贡献都一样。工具结果之后的理解、是否继续调用工具、如何选择公式，通常比连接词和模板句更关键。用熵调节 advantage，可以让高不确定性位置获得更合适的学习信号。

  0.2 应该说成经验超参，而不是理论最优值。更成熟的方案可以根据 KL、clipfrac、entropy 分布或验证 reward 自适应调整。若面试官问 ablation，要诚实说明完整拆解仍需补实验。
follow_up_questions:
  - entropy std 为 0 怎么办？
  - 为什么不用 entropy 直接加 loss？
follow_up_answer_points:
  - std 为 0 时做兜底，避免除零。
  - 直接 entropy loss 是鼓励随机性，这里是调节已有 reward 信号。
pitfalls:
  - 不要说 0.2 是理论推导出的最优值。
  - 不要说高熵一定放大到固定 1.2 倍，标准化值会随 batch 变化。
fact_status: confirmed
related_chunks: [KB-RL-005, KB-ENT-001, KB-FACT-002]
---

---
chunk_id: KB-ENT-004
title: Dynamic Rollout 与分支采样
category: entropy
tags: [Dynamic Rollout, beam branching, rollout, branch_probability, 工具调用成本]
aliases: [动态采样, 分支采样, 高熵分支]
trigger_questions:
  - Dynamic Rollout 是什么？
  - 为什么要做分支采样？
short_answer: |
  Dynamic Rollout 的目标是在生成阶段更聪明地分配采样预算，而不是每个 prompt 固定生成同样多轨迹。项目支持 initial_rollouts、rollout n、beam_size、branch_probability 等参数，让仍然活跃、可能有信息增益的轨迹 fork 出分支继续探索。它要和工具去重、循环检测、call limit 一起使用，否则工具调用成本会失控。
deep_answer: |
  Agent rollout 很贵，因为每条轨迹可能多轮生成，还会调用搜索或 Python。简单题不需要很多分支，复杂题如果只采样一条又容易错过更好的路径。动态分支的直觉是把预算投给不确定性更高、仍有希望改进 reward 的位置。

  不同文档对分支概率细节表述不完全一致，所以面试中讲机制目的更稳：提高有效探索、减少无效重复调用、让高不确定性位置有更多候选轨迹。具体公式和开关应以实际训练配置为准。
follow_up_questions:
  - 分支采样会不会导致 API 调用爆炸？
  - 动态 rollout 每次实验都开了吗？
follow_up_answer_points:
  - 用去重、缓存、循环检测、call limit、timeout 控制成本。
  - 项目支持该机制，具体实验是否启用要看脚本配置。
pitfalls:
  - 不要把 Dynamic Rollout 说成已经证明最优的采样策略。
  - 不要死背旧文档里不完全一致的分支公式。
fact_status: mixed
related_chunks: [KB-AGENT-004, KB-DIST-002, KB-FACT-002]
---

---
chunk_id: KB-ENT-005
title: 熵相关裁剪的谨慎口径
category: entropy
tags: [entropy clipping, PPO clipping, ratio.detach, policy update, 稳定性]
aliases: [自适应裁剪, 熵裁剪, clipping机制]
trigger_questions:
  - ARAEPO 的 clipping 怎么讲？
  - 熵是否直接决定 clip 上下界？
short_answer: |
  最稳妥说法是：项目有熵相关的 policy update 稳定机制，会与 entropy-aware advantage、PPO ratio clipping 和 dual-clip 组合使用，用于控制更新行为和梯度稳定性。当前可见实现中的裁剪公式不应被说成“clip 上下界直接由 entropy 数值逐 token 决定”。真正直接使用 token entropy 的明确机制是 entropy-aware advantage。
deep_answer: |
  标准 PPO 用 `ratio = exp(log_prob_new - log_prob_old)` 控制新旧策略变化。项目中的变体在打开开关时使用带 `ratio.detach()` 的上界表达式，并继续使用 dual-clip 处理负 advantage 样本。`detach()` 的价值是让边界控制参与前向计算，但不让边界本身引入不稳定梯度路径。

  如果面试官追问代码细节，可以说：我会把裁剪机制讲成 policy update 阶段的稳定性设计，而不是把它夸大成完全由 entropy 驱动的逐 token clip。这个口径更符合当前核查结果。
follow_up_questions:
  - 为什么还需要 dual-clip？
  - clipfrac 怎么看？
follow_up_answer_points:
  - dual-clip 限制负 advantage 样本导致的过度惩罚。
  - clipfrac 过高说明更新太猛，过低可能学习不足。
pitfalls:
  - 不要说“高熵 token 的 clip 上界一定更大”。
  - 不要把支持开关说成完整消融证明。
fact_status: confirmed
related_chunks: [KB-ENT-003, KB-ENT-006, KB-FACT-002]
---

---
chunk_id: KB-ENT-006
title: Dual-Clip 与 NaN 风险
category: entropy
tags: [Dual-Clip PPO, NaN, grad_norm, entropy_std, 梯度稳定, clip_ratio_c]
aliases: [训练稳定性, 梯度爆炸, loss NaN]
trigger_questions:
  - 训练中怎么防止 NaN？
  - Dual-Clip 的作用是什么？
short_answer: |
  Dual-Clip 在 PPO clip 之外对负 advantage 样本再加一层限制，避免差轨迹被过度惩罚导致更新不稳定。项目还依赖 entropy std 兜底、grad norm 裁剪、finite 检测、KL、mask、dynamic micro batch 和 checkpoint resume 共同控制风险。Agent RL 的长轨迹、工具失败和 ratio 极端值都可能诱发 NaN 或 loss spike。
deep_answer: |
  熵感知 advantage 需要 `(entropy - mean) / std`，如果某个 batch 的 entropy 分布极端或 std 接近 0，就可能造成 advantage 缩放异常。代码层面有 std 为 0 的保护，但极端长序列仍可能带来 loss 尖峰。

  面试时可以把稳定性讲成组合拳：算法上有 clip、dual-clip、KL 和 detach；数据上有 mask 和分组归一化；系统上有 dynamic batch 和 sequence balancing；工具上有 timeout、重试和循环终止。
follow_up_questions:
  - grad_norm 非有限怎么办？
  - loss spike 一定是数据问题吗？
follow_up_answer_points:
  - 跳过本次更新、清梯度，并检查 ratio、entropy、tokenizer、mask 和工具轨迹。
  - 不一定，可能是熵分布、长序列、显存状态或工具异常。
pitfalls:
  - 不要说 Dual-Clip 是本项目原创算法。
  - 不要只用 loss 判断训练是否健康，要结合 reward、KL、entropy 和工具指标。
fact_status: confirmed
related_chunks: [KB-RL-006, KB-DIST-003, KB-AGENT-005]
---

## 05 Agent 工程

---
chunk_id: KB-AGENT-001
title: ToolAgent 状态机
category: agent
tags: [ToolAgent, 状态机, vLLM, ReAct, tool calling, 多轮推理]
aliases: [工具调用怎么实现, vLLM能不能做Agent, Agent状态]
trigger_questions:
  - 多工具 Agent 怎么实现？
  - vLLM 为什么不能直接做 Agent？
short_answer: |
  vLLM 是高吞吐推理引擎，本身不管理多轮工具状态。项目在 vLLM 外层封装 ToolAgent：模型生成到工具停止标签时暂停，解析工具内容，调用对应工具，把结果包装后拼回上下文，再继续生成。状态机要追踪当前输入、初始 prompt、工具调用次数、是否结束、活跃样本、工具历史和 result mask。
deep_answer: |
  Agent 轨迹是一个循环：生成一段、判断是否触发工具、执行工具、追加结果、继续生成，直到 EOS、长度上限、call limit 或循环终止。不同样本轮数不同，所以需要 active indices 和 dones 管理哪些样本还活着。

  工具返回不是模型自己生成的动作，通常要通过 mask 排除出 policy loss。否则模型会被训练去复现工具输出，而不是学习“什么时候调用工具以及如何使用工具结果”。
follow_up_questions:
  - 如何判断工具调用结束？
  - 工具结果如何进入上下文？
follow_up_answer_points:
  - 通过工具标签闭合或 stop sequence 识别。
  - 包装成 result 片段追加到 token 序列，并更新 mask。
pitfalls:
  - 不要说 vLLM 自带完整 Agent 状态机。
  - 不要忽略工具返回 token 的 mask。
fact_status: confirmed
related_chunks: [KB-RL-005, KB-AGENT-004, KB-DIST-002]
---

---
chunk_id: KB-AGENT-002
title: 搜索工具
category: agent
tags: [Search Tool, BingSearchTool, BrightData, cache, 搜索, API]
aliases: [搜索怎么接入, 搜索缓存, BrightData]
trigger_questions:
  - 搜索工具怎么接入？
  - 怎么减少重复搜索？
short_answer: |
  搜索工具通过模型生成搜索标签触发，外部调用搜索 API，把摘要结果返回给模型继续推理。工程重点不是“搜得越多越好”，而是稳定、可控、可复现：需要缓存、并发控制、超时、重试、结果长度限制和 API key 保护。搜索缓存和 ToolAgent 去重配合，可以减少重复请求和训练成本。
deep_answer: |
  Agent RL 中多个分支可能搜索同一个 query，或者模型反复改写近似 query。如果每次都真实调用 API，成本、延迟和限流风险都会很高。缓存与去重可以把相同工具和相同内容的请求合并，并提升复现性。

  搜索结果应以短摘要形式进入上下文，避免把完整网页塞进 prompt 导致序列过长。训练时还要监控工具成功率、平均耗时、失败数和重试次数，以区分模型能力问题和外部服务问题。
follow_up_questions:
  - 搜索失败怎么办？
  - 搜索缓存会不会污染训练？
follow_up_answer_points:
  - 失败时重试、返回错误文本、复用缓存或终止异常轨迹。
  - 缓存提高复现性，但需要刷新策略和 query 规范。
pitfalls:
  - 不要暴露 API key 或真实凭证。
  - 不要把搜索缓存说成完整 RAG 向量库。
fact_status: confirmed
related_chunks: [KB-AGENT-004, KB-AGENT-005, KB-PRESS-007]
---

---
chunk_id: KB-AGENT-003
title: Python 工具边界
category: agent
tags: [Python Tool, subprocess, conda, timeout, sandbox, 金融计算]
aliases: [代码解释器, Python安全吗, 工具安全]
trigger_questions:
  - Python 工具怎么实现？
  - Python 工具安全吗？
short_answer: |
  Python 工具通过模型生成代码标签触发，用指定 conda 环境的 Python 子进程执行代码，并返回 stdout 或错误信息。它适合数学计算、矩阵运算和未来金融建模，但当前更准确地说是“子进程执行加 timeout”，不能夸大为生产级安全沙箱。生产化需要容器隔离、资源限制、网络限制、文件系统权限和审计日志。
deep_answer: |
  当前实现比主进程直接 eval 更稳，因为工具执行在子进程中，有 timeout 兜底，异常也可以作为错误文本返回给模型。但 subprocess 不是强隔离：死循环、子进程的子进程、大内存分配和文件系统访问都需要额外控制。

  对金融任务来说，Python 工具很有潜力，例如 pandas 财务建模、Monte Carlo、组合优化和复杂公式计算。不过这些属于后续优化方向，当前金融评估主要是独立 QA 和 rule-based 评估，不应说成已经完整实现多轮金融建模 Agent。
follow_up_questions:
  - 如何防止恶意代码？
  - Python 超时后怎么办？
follow_up_answer_points:
  - 生产环境用容器或远程 sandbox，限制网络、文件、CPU、内存和运行时长。
  - 超时返回错误或终止轨迹，并记录工具失败指标。
pitfalls:
  - 不要说当前 PythonTool 达到生产级安全隔离。
  - 不要把未来 pandas 财务建模说成已完成。
fact_status: confirmed
related_chunks: [KB-PRESS-007, KB-FIN-006]
---

---
chunk_id: KB-AGENT-004
title: 去重、循环检测与重试
category: agent
tags: [dedup, loop detection, retry, exponential backoff, call limit, 工具稳定性]
aliases: [工具失败处理, 重复调用, 死循环]
trigger_questions:
  - 工具调用失败怎么处理？
  - 如何避免 Agent 一直搜索同一个问题？
short_answer: |
  项目做了三类稳定性处理：工具调用去重，用工具名和内容 hash 识别重复请求并复用结果；循环检测，连续多次调用同一工具且 query 相似时终止轨迹；指数退避重试，外部 API 失败时按递增延迟重试。这些机制主要解决成本、延迟、限流和死循环问题。
deep_answer: |
  Beam branching 会让多个分支共享前缀，容易同时触发相同搜索或 Python 计算。去重能把相同请求合并，避免重复 API 调用。循环检测针对另一类问题：模型陷入“搜 A、再搜 A 的变体、继续搜 A”的局部循环，浪费 rollout 预算。

  指数退避比立即重试更适合限流和网络抖动，因为外部服务短时间内可能不可用。重试失败后可以返回错误文本、终止轨迹或记录失败指标，具体是否给负 reward 要看任务设计。
follow_up_questions:
  - 去重会不会影响探索？
  - API 调用降低 15-30% 能说吗？
follow_up_answer_points:
  - 去重只复用相同请求，不阻止不同策略路径。
  - 15-30% 是文档经验口径，建议说“能减少重复调用”，不要当硬结果。
pitfalls:
  - 不要把经验数字当成经过完整实验验证的主结果。
  - 循环检测阈值要避免误杀正常多步搜索。
fact_status: mixed
related_chunks: [KB-ENT-004, KB-AGENT-005, KB-FACT-002]
---

---
chunk_id: KB-AGENT-005
title: Agent 监控与降级
category: agent
tags: [monitoring, AgentMetrics, tool success rate, branch efficiency, failure degradation]
aliases: [工具监控, 训练健康度, 失败降级]
trigger_questions:
  - Agent 训练怎么监控？
  - 如何判断工具调用是否正常？
short_answer: |
  Agent 训练不能只看 reward 和 loss，还要看工具调用总数、成功率、失败数、平均执行时间、最大重试、call limit 命中、去重次数、分支来源、循环终止和 unique queries。失败降级包括返回错误文本、复用缓存、终止异常轨迹或跳过无效更新。这样才能区分模型不会做题和工具系统不稳定。
deep_answer: |
  在 Agent RL 中，reward 下降可能来自模型推理差，也可能来自搜索 API 超时、Python 工具异常、工具标签格式错、mask 错或分支状态不同步。增强监控能定位这些问题。

  例如工具调用率升高但 reward 不升，可能是模型滥用工具；工具成功率低，可能是外部服务或凭证问题；branch/from_restart 高，说明很多轨迹走死后重启，分支效率差；loop terminations 高，说明模型在重复查询。
follow_up_questions:
  - 哪些指标说明训练不健康？
  - 失败轨迹要不要训练？
follow_up_answer_points:
  - KL 爆、clipfrac 高、entropy 归零、工具失败率高、循环终止多都可疑。
  - 明显环境失败应标记处理，避免模型学到错误惩罚。
pitfalls:
  - 不要只用 loss 判断 Agent RL 是否正常。
  - 不要把外部工具失败误判成模型能力下降。
fact_status: confirmed
related_chunks: [KB-ENT-006, KB-DIST-003, KB-PRESS-003]
---

## 06 分布式训练与系统工程

---
chunk_id: KB-DIST-001
title: Ray 编排
category: distributed
tags: [Ray, WorkerGroup, ResourcePool, Role, ActorRollout, RefPolicy, Critic]
aliases: [Ray架构, Worker角色, ResourcePool]
trigger_questions:
  - Ray 分布式架构怎么设计？
  - Ray 和 Kubernetes 或 torchrun 有什么区别？
short_answer: |
  项目用 Ray 管理分布式 worker 和 GPU 资源，把 ActorRollout、Critic、RefPolicy、RewardModel 等角色映射到不同 WorkerGroup。GRPO 场景通常不需要 critic，PPO/GAE 场景才会启用 value worker。Ray 的价值是任务级调度、GPU 感知、远程调用和资源池管理，而不是替代 FSDP 或张量并行本身。
deep_answer: |
  RayPPOTrainer 类似 driver，编排数据加载、rollout、reward、advantage、log_prob、actor update 和 checkpoint。真正的大模型计算在 worker 上执行。ActorRollout 是关键角色，既要配合 vLLM 生成，又要配合 FSDP 更新 actor。

  Kubernetes 更偏容器和集群运维，torchrun 更偏静态分布式训练启动。Ray 更适合这种有多种角色、远程任务和动态资源调度的 RL 训练系统。
follow_up_questions:
  - GRPO 下为什么没有 critic？
  - worker 失败怎么办？
follow_up_answer_points:
  - GRPO 用组内 baseline，不训练独立 value model。
  - Ray 有一定容错，但训练状态仍要依赖 checkpoint 恢复。
pitfalls:
  - 不要说所有 Role 都一定启用，取决于算法和配置。
  - 不要把 Ray 当成模型并行算法。
fact_status: confirmed
related_chunks: [KB-DIST-002, KB-RL-002, KB-DIST-005]
---

---
chunk_id: KB-DIST-002
title: vLLM、FSDP 与 HybridEngine
category: distributed
tags: [vLLM, FSDP, HybridEngine, KV cache, gpu_memory_utilization, 显存]
aliases: [vLLM和FSDP协同, 显存分配, 混合引擎]
trigger_questions:
  - vLLM 和 FSDP 怎么协同？
  - 训练时显存怎么分配？
short_answer: |
  vLLM 负责高吞吐 rollout，FSDP 负责训练和梯度同步。HybridEngine 的核心是在生成阶段让 vLLM 使用权重和 KV cache，在训练阶段切回 FSDP 做 log_prob、loss 和 optimizer step。`gpu_memory_utilization` 设太高会挤占训练显存，太低会降低 rollout 吞吐，所以要结合 batch、序列长度、模型大小调。
deep_answer: |
  纯 vLLM 不能完成 RL 训练，因为它主要是推理引擎，不负责反向传播、优势估计和优化器更新。纯 FSDP 可以训练，但自回归 rollout 吞吐不如 vLLM，特别是 Agent 长序列和多轮工具调用会让生成成为主要瓶颈。

  显存状态大致在 vLLM 推理、KV cache 释放、FSDP 前向反向、梯度和激活释放之间切换。如果 cache 或分片状态没有管理好，下一步很容易 OOM。
follow_up_questions:
  - 为什么 vLLM 不能直接做 Agent？
  - 推理训练能否完全并行？
follow_up_answer_points:
  - 工具调用需要外层状态机，vLLM 不管理工具状态。
  - 有 sync 和 async 模式，但权重版本、显存和数据一致性会限制并行度。
pitfalls:
  - 不要说 vLLM 和 FSDP 同一时刻都满负载。
  - 不要忽略 KV cache 对长上下文 Agent 的显存压力。
fact_status: confirmed
related_chunks: [KB-AGENT-001, KB-DIST-006, KB-ENT-004]
---

---
chunk_id: KB-DIST-003
title: Sequence Balancing 与 Dynamic Micro Batch
category: distributed
tags: [sequence balancing, dynamic micro batch, token balance, long sequence, OOM]
aliases: [长短序列不均, token级负载均衡, dynamic bsz]
trigger_questions:
  - 为什么 Agent RL 需要 sequence balancing？
  - dynamic micro batch 是什么？
short_answer: |
  Agent 轨迹长度差异很大，有的样本不调工具很短，有的多轮搜索和 Python 计算很长。如果按样本数平均分给 GPU，会出现某些 GPU 处理大量 token、其他 GPU 等待的问题。Sequence balancing 按有效 token 数重排 batch，dynamic micro batch 按每 GPU 最大 token 数切分，减少 OOM 和显存浪费。
deep_answer: |
  大模型训练的计算量主要由 token 数决定，不是样本条数。Agent RL 又会因为工具调用和分支采样放大长度差异。项目通过 attention mask 统计有效长度，再按 worker 数做平衡分区。

  Actor update 时，如果开启 dynamic batch，会根据最大 token 长度组织 micro batch：长样本少放、短样本多放。这样能更充分利用显存，但要求 uid、mask、meta_info 在重排后不丢失。
follow_up_questions:
  - 重排会影响 GRPO 分组吗？
  - 什么时候不用 dynamic batch？
follow_up_answer_points:
  - 保留 uid 后不会影响同 prompt 分组。
  - 小模型或长度均匀时固定 batch 更简单。
pitfalls:
  - 不要按样本数理解训练负载，token 数更关键。
  - dynamic batch 更复杂，必须保证 mask 和分组信息正确。
fact_status: confirmed
related_chunks: [KB-RL-005, KB-DIST-004, KB-AGENT-005]
---

---
chunk_id: KB-DIST-004
title: DataProto 数据协议
category: distributed
tags: [DataProto, TensorDict, non_tensor_batch, meta_info, 数据协议, mask]
aliases: [训练数据怎么传, TensorDict, batch协议]
trigger_questions:
  - DataProto 是什么？
  - 为什么不用普通 dict？
short_answer: |
  DataProto 是项目里跨模块传递训练数据的统一协议，核心由三部分组成：batch 放 TensorDict，比如 input_ids、attention_mask、responses、old_log_probs、advantages；non_tensor_batch 放 uid、raw prompt、extra_info 等非 tensor 信息；meta_info 放 temperature、micro_batch_size、max_token_len 等运行时参数。它适合切片、concat、repeat、reorder 和分布式传输。
deep_answer: |
  PPO/GRPO 训练中，同一个 batch 会经历 rollout、reward、log_prob、advantage 和 update_actor 多个阶段。如果每一步都用普通 dict，字段容易丢，维度容易错，也不方便在 worker 间传递。

  DataProto 的另一个价值是处理多采样。一个 prompt 生成 n 条 response 后，需要 repeat 原 prompt 并保留 uid，后续才能做 GRPO 组内 advantage。meta_info 中的 temperature 等参数也会影响 log_prob 计算，不能丢。
follow_up_questions:
  - uid 为什么重要？
  - non_tensor_batch 会不会拖慢训练？
follow_up_answer_points:
  - uid 用于同 prompt 分组和重排后恢复归属。
  - 非 tensor 信息不参与 GPU 计算，但对分组、调试和评估必要。
pitfalls:
  - 不要把所有信息都塞进 tensor batch。
  - 不要在 sequence balancing 后丢失 uid。
fact_status: confirmed
related_chunks: [KB-RL-005, KB-DIST-003, KB-FIN-002]
---

---
chunk_id: KB-DIST-005
title: Checkpoint 与部署转换
category: distributed
tags: [checkpoint, resume, FSDP checkpoint, HuggingFace, vLLM, dataloader state]
aliases: [断点续训, FSDP分片, ckpt转HF]
trigger_questions:
  - Checkpoint 怎么保存和恢复？
  - FSDP checkpoint 能直接部署吗？
short_answer: |
  项目 checkpoint 会保存 actor 参数、可选 critic 参数、优化器状态和 dataloader 状态，并记录 global step。恢复训练不能只加载模型，还要恢复 dataloader，否则数据顺序可能改变。FSDP checkpoint 是分片格式，通常不能直接给 vLLM 部署，需要先合并转换成 HuggingFace 格式，再检查 tokenizer、config 和 chat template。
deep_answer: |
  断点续训的难点是训练状态一致性。模型权重恢复了，但如果数据文件变了、排序变了或 dataloader 偏移错了，可能导致样本重复训练或被跳过。项目文档强调 checkpoint 中会包含 dataloader state，就是为了解决这类问题。

  部署转换也常被问：FSDP 为训练节省显存，把参数切在多个 rank 上；推理时 vLLM 或 transformers 需要完整权重、配置和 tokenizer，因此要做 merge，再用少量样本验证输出格式。
follow_up_questions:
  - 8 卡 checkpoint 能直接 4 卡加载吗？
  - 只保存 actor 可以吗？
follow_up_answer_points:
  - 通常需要先合并再重新分片，不能简单直接加载。
  - GRPO 主要关心 actor，PPO/GAE 还要考虑 critic。
pitfalls:
  - 不要说 FSDP 分片 checkpoint 可以直接 vLLM 加载。
  - 不要忽略 tokenizer 和 chat template 一致性。
fact_status: confirmed
related_chunks: [KB-DIST-001, KB-FIN-003]
---

---
chunk_id: KB-DIST-006
title: Sync 与 Async Rollout
category: distributed
tags: [sync rollout, async rollout, AsyncLLMServerManager, wake sleep, rollout efficiency]
aliases: [同步异步rollout, wake sleep, 推理训练并行]
trigger_questions:
  - Async Rollout 是什么？
  - sync 和 async 有什么区别？
short_answer: |
  Sync rollout 是生成完一批轨迹后再训练，流程简单、稳定、容易调试。Async rollout 试图让生成和训练更并行，通过异步管理 vLLM 服务的 wake/sleep，减少 GPU 空闲。Async 的吞吐潜力更高，但会带来策略版本、log_prob、reward、batch 对齐和工具状态同步问题。
deep_answer: |
  Agent RL 的瓶颈经常在 rollout，因为自回归生成慢，工具调用还有外部延迟。Async 的目标是减少等待时间，让推理和训练资源更充分利用。

  但 async 更容易引入 off-policy 或状态不一致：一批样本可能由旧策略生成，却用新策略更新；工具结果的返回时间也不一致。对于复现实验和 debug，sync_with_tool 更容易控制；系统稳定后再考虑 async 提吞吐。
follow_up_questions:
  - Async 会不会造成 off-policy 问题？
  - 什么时候值得用 async？
follow_up_answer_points:
  - 策略版本滞后太多时需要考虑 off-policy 偏差。
  - 当 rollout 成为瓶颈且系统稳定后再启用。
pitfalls:
  - 不要说 async 一定更好，它更快但更复杂。
  - 不要忽略工具调用带来的额外同步问题。
fact_status: confirmed
related_chunks: [KB-DIST-002, KB-AGENT-001]
---

## 07 金融经济领域扩展

---
chunk_id: KB-FIN-001
title: 8 子领域数据构建
category: finance
tags: [金融经济, finance, economics, 8子领域, CFA, 4239 QA]
aliases: [金融数据怎么构建, 领域划分, 数据规模]
trigger_questions:
  - 金融数据怎么构建的？
  - 8 个子领域是什么？
short_answer: |
  金融经济数据按 8 个子领域构建，总计 4239 条 QA：宏观经济与政策 747、投资与组合管理 681、公司金融与估值 679、银行与货币市场 610、微观经济学 560、金融数学 374、财务报表分析 329、金融监管与合规 259。划分参考 CFA 和金融经济知识体系，因为不同领域对应不同推理类型。
deep_answer: |
  数据不是简单堆题，而是为了适配 RL 训练和评估。宏观和财报更偏公式计算，公司金融更偏估值建模，投资组合涉及矩阵和风险指标，银行货币市场涉及久期和利率，监管合规偏概念记忆，金融数学偏衍生品公式。

  数据构成包括核心题、模板化数值变体和概念分析题。模板化变体能帮助模型学习 WACC、NPV、CAPM、久期等通用计算方法，但真实业务多样性不足，所以后续仍需要公开数据和真实财报任务补充。
follow_up_questions:
  - 模板化数据会不会过拟合？
  - 为什么监管样本少？
follow_up_answer_points:
  - 有过拟合风险，需要 held-out 模板和真实案例评估。
  - 监管概念题不适合无限数值变体，可生成空间更小。
pitfalls:
  - 不要说 4239 条足以覆盖全部金融知识。
  - 不要把总 QA 数说成训练集行数。
fact_status: confirmed
related_chunks: [KB-FIN-002, KB-PRESS-002]
---

---
chunk_id: KB-FIN-002
title: Parquet Schema 与 Reward Model
category: finance
tags: [Parquet, schema, reward_model, ground_truth, prompt, finance_train]
aliases: [金融数据格式, reward_model字段, 训练数据列]
trigger_questions:
  - 金融数据怎么保证符合训练格式？
  - reward_model 里放什么？
short_answer: |
  金融训练数据 `finance_train.parquet` 已核对为 3391 行、5 列：`data_source`、`prompt`、`ability`、`reward_model`、`extra_info`；验证集 `finance_valid.parquet` 为 508 行。`prompt` 是角色对话列表，`ability` 标记金融子领域，`reward_model` 包含 rule 风格和 ground truth，`extra_info` 放 split、domain、difficulty 等元信息。
deep_answer: |
  这个 schema 的价值是直接兼容现有 RL 管线。DataLoader 读取 prompt，reward 计算读取 ground truth，extra_info 支持按领域和难度分析。金融数据不是新建一套孤立流程，而是复用项目已有的 Parquet 训练接口和 JSONL 评估接口。

  需要谨慎的是：reward_model 包含完整分步答案，有利于后续步骤级评分，但当前口径不能夸大成已经实现了成熟过程奖励。当前主要还是 rule-based ground truth、数值容差、F1 或关键点匹配。
follow_up_questions:
  - 为什么用 Parquet 而不是 JSON？
  - 完整解答有什么用？
follow_up_answer_points:
  - Parquet 列式读取更适合训练数据，schema 清晰。
  - 完整解答可支持未来步骤级 reward 和错误分析。
pitfalls:
  - 不要说当前已经有完善的步骤级金融 reward。
  - 不要漏掉 `reward_model` 和 `extra_info` 对训练评估的重要性。
fact_status: confirmed
related_chunks: [KB-RL-003, KB-DIST-004, KB-FIN-006]
---

---
chunk_id: KB-FIN-003
title: 三层评估与结果
category: finance
tags: [finance eval, FinBench, 77.6, 45.5, 73.8, 1020题]
aliases: [金融评估结果, 金融综合准确率, FinBench结果]
trigger_questions:
  - 金融评估怎么设计？
  - 金融结果是多少？
short_answer: |
  金融评估采用三层结构：finance 综合评估 340 题，看整体能力；FinBench 高难基准 200 题，看推理上限；8 个领域专项各 60 题，共 480 题，看细粒度短板，总计 1020 题。统一结果口径是：金融综合 77.6%，FinBench 高难 45.5%，8 领域专项平均 73.8%。
deep_answer: |
  按难度拆分：easy 89.4%，medium 76.2%，hard 58.7%。按领域拆分：宏观经济与政策 82.1%，财务报表分析 79.5%，公司金融与估值 77.8%，投资与组合管理 71.3%，微观经济学 70.5%，银行与货币市场 66.2%，金融数学 63.4%，金融监管与合规 59.8%。

  结果说明模型在公式固定、计算明确的任务上更强，在监管概念、高难金融数学和复杂估值任务上较弱。FinBench 45.5% 不是要包装成强结果，而是明确暴露高难场景短板。
follow_up_questions:
  - 为什么旧摘要低口径不采用？
  - 77.6% 可靠吗？
follow_up_answer_points:
  - 旧摘要低口径与后续金融文档冲突，最终统一采用金融文档和核对口径 77.6%。
  - 计算题更可靠，概念题仍需 LLM-as-judge 或人工抽样校验。
pitfalls:
  - 不要混用旧摘要低口径。
  - 不要只报总分不讲高难和领域短板。
fact_status: confirmed
related_chunks: [KB-FACT-001, KB-PRESS-003, KB-FIN-004]
---

---
chunk_id: KB-FIN-004
title: 结果分析与短板
category: finance
tags: [结果分析, 金融监管, 金融数学, hard, rule-based评估, 短板]
aliases: [为什么监管低, 为什么金融数学低, 结果怎么解释]
trigger_questions:
  - 为什么监管和金融数学表现较差？
  - FinBench 高难只有 45.5% 怎么解释？
short_answer: |
  监管类问题多是 Basel III、Dodd-Frank、反洗钱、合规条文等概念记忆和开放表述，rule-based 或关键词评分信号较弱，所以金融监管只有 59.8%。金融数学涉及 Black-Scholes、二叉树、久期凸性、Monte Carlo 等公式细节，模型容易在公式记忆和数值代入上出错，所以金融数学为 63.4%，FinBench 高难为 45.5%。
deep_answer: |
  这个结果符合任务特性：宏观和财报很多是固定公式和分步计算，reward 信号明确；监管和复杂金融数学更依赖知识记忆、公式细节、开放解释和复杂中间步骤，当前数据和评估都更难给出稳定反馈。

  改进方向包括提高高难题覆盖、增加公式变体、引入 Python 工具做精确计算、对概念题引入 LLM-as-judge、加入公开真实金融数据和中文金融数据。注意这些属于未来优化，不是当前已经完成的实验结果。
follow_up_questions:
  - 这说明项目失败了吗？
  - 怎么提升监管题？
follow_up_answer_points:
  - 不是失败，而是三层评估暴露了可优化方向。
  - 监管题需要更好数据、judge rubric、同义表达评分和真实法规场景。
pitfalls:
  - 不要把低分领域轻描淡写。
  - 不要说 LLM-as-judge 已经作为当前主评估。
fact_status: confirmed
related_chunks: [KB-FIN-006, KB-PRESS-003]
---

---
chunk_id: KB-FIN-005
title: 为什么不直接用公开金融数据集
category: finance
tags: [公开金融数据, FinQA, ConvFinQA, FLARE-FinQA, 生成数据, 数据清洗]
aliases: [为什么自己生成数据, 公开数据不用吗, FinQA]
trigger_questions:
  - 为什么不直接用公开金融数据集训练？
  - 自己生成数据有效吗？
short_answer: |
  不是不用公开数据，而是当前阶段先用可控生成数据跑通训练和评估闭环。FinQA、ConvFinQA 等公开数据多是财报阅读理解，任务形式和项目需要的独立多步计算、工具调用、rule-based reward 不完全匹配；很多样本缺少完整分步推导、难度标注和统一 system prompt。后续应导入公开数据，但要先补推理链、标领域难度、统一 schema 并去重。
deep_answer: |
  生成数据的优势是 schema 精确、ground truth 完整、难度可控，适合验证 RL 管线和 reward。缺点是真实业务多样性不足，模板化变体可能导致模型学到题型模式而不是泛化能力。

  最稳回答是：生成数据是 Phase 1，不是最终答案。Phase 2 应该混入公开金融数据、真实财报、市场数据和中文金融数据，并设计 held-out 模板、真实案例和人工抽样评估，防止模板过拟合。
follow_up_questions:
  - 如何防止模板过拟合？
  - 公开数据怎么清洗？
follow_up_answer_points:
  - 按模板、题型、领域隔离 held-out，换参数和表述测试泛化。
  - 补 chain-of-thought、system prompt、difficulty、schema，去重并过滤低质量样本。
pitfalls:
  - 不要否认生成数据局限。
  - 不要说公开金融数据已经大规模导入当前训练。
fact_status: confirmed
related_chunks: [KB-FIN-001, KB-PRESS-002]
---

---
chunk_id: KB-FIN-006
title: 金融 Reward 与未来工具任务
category: finance
tags: [金融 reward, LLM-as-judge, Python工具, 实时行情, pandas, future direction]
aliases: [金融reward怎么改, 未来优化, 金融Agent]
trigger_questions:
  - 金融 reward 怎么设计？
  - 后续如何提升金融能力？
short_answer: |
  当前金融评估对数值题主要依赖 rule-based 比对和容差，对概念题依赖 F1 或关键点匹配。这对 NPV、WACC、CAPM、久期等计算题有效，但对监管合规和开放分析不够细。后续金融 reward 应同时考虑数值精度、单位、推理步骤、关键概念覆盖、合规表述，并对概念题引入 LLM-as-judge。
deep_answer: |
  未来更像真正金融 Agent 的方向，是把搜索和 Python 工具接入金融任务：搜索实时行情、宏观数据或公司财报，用 Python/pandas 做财务建模、组合优化、Monte Carlo 或敏感性分析。但这些会带来可复现性、数据时效、工具安全、评估一致性和成本问题。

  面试中要明确区分：当前已经完成的是静态金融 QA 数据、训练格式适配和三层评估；实时行情、多轮工具任务、pandas 建模、LLM-as-judge 主评估和中文金融数据是后续优化方向。
follow_up_questions:
  - 为什么数值题用 ±1%？
  - LLM-as-judge 有什么风险？
follow_up_answer_points:
  - ±1% 适配浮点和四舍五入，但不同题型应调整。
  - judge 有成本、偏差和一致性问题，需要 rubric 和抽样校验。
pitfalls:
  - 不要说当前金融 reward 已经完全理解步骤质量。
  - 不要把实时工具任务说成已完成成果。
fact_status: future_direction
related_chunks: [KB-RL-003, KB-AGENT-003, KB-SCOPE-002]
---

## 08 AI Agent 技术面试官视角扩充

---
chunk_id: KB-TECH-001
title: 算法追问集合
category: pressure
tags: [技术追问, PPO, GRPO, critic, outcome reward, SFT, KL]
aliases: [算法面试追问, RL追问, 面试官会问什么]
trigger_questions:
  - 面试官会怎么追问算法？
  - GRPO 不用 critic 怎么回答？
short_answer: |
  算法追问通常集中在：为什么不用 PPO、GRPO 不用 critic 怎么做信用分配、outcome reward 的局限、SFT 冷启动必要性、KL 和 entropy 的区别。回答主线是：本项目任务多是最终答案级 reward，GRPO 通过同 prompt 多采样做相对优势，省 critic 显存；SFT 先学工具协议，RL 再学工具决策；KL 控制策略偏移，entropy 识别不确定性。
deep_answer: |
  如果被问“GRPO 会不会粗糙”，要承认它对过程信用分配不如密集 reward 或 critic，但适合当前答案可验证、显存敏感、rollout 成本高的 Agent 任务。未来可用过程 reward、步骤级评分或 critic 对照增强。

  如果被问“outcome reward 有什么问题”，要说它无法精确定位中间错误，可能鼓励捷径或模板记忆。金融场景尤其需要数值、单位、步骤和概念覆盖多维评分。
follow_up_questions:
  - PPO 是否应作为对照？
  - SFT 后为什么还要 RL？
follow_up_answer_points:
  - PPO/GAE 可以作为对照，尤其在需要 critic 的任务上。
  - SFT 是模仿工具格式，RL 是按 reward 优化策略。
pitfalls:
  - 不要把 GRPO 说成所有任务都更强。
  - 不要否认 outcome reward 的信用分配局限。
fact_status: confirmed
related_chunks: [KB-RL-002, KB-RL-003, KB-RL-004]
---

---
chunk_id: KB-TECH-002
title: 熵机制追问集合
category: pressure
tags: [技术追问, entropy, 高熵, 熵权重, ablation, clipping]
aliases: [熵追问, 高熵是不是高价值, 熵权重0.2]
trigger_questions:
  - 高熵是不是等于高价值？
  - 熵机制会不会鼓励胡乱探索？
short_answer: |
  高熵不等于高价值，它表示模型不确定，可能是工具返回后的关键信息整合点，也可能只是混乱。熵机制的合理解释是“用不确定性辅助分配采样预算和训练权重”，而不是直接奖励随机性。熵权重 0.2 是经验超参，后续可以根据 KL、clipfrac、entropy 分布和验证 reward 做自适应。
deep_answer: |
  如果被问 ablation，要诚实说：机制和开关已经接入，但完整 ablation 需要按 Dynamic Rollout、Entropy-Aware Advantage、裁剪稳定机制、Agent 工程优化分别拆解。没有完整表格时，不要硬编每个机制提升多少。

  如果被问 clipping，要用谨慎口径：可确认 token entropy 直接用于 advantage 重加权；当前可见裁剪公式不应被说成 clip 上下界逐 token 直接由 entropy 数值决定。
follow_up_questions:
  - 怎么防止过探索？
  - 没有完整 ablation 怎么回答？
follow_up_answer_points:
  - 用 KL、clip、call limit、branch 上限、去重和循环检测控制。
  - 承认不足，给出消融设计：逐个开关、固定数据和 seed、比较 reward/工具调用/稳定性。
pitfalls:
  - 不要说高熵 token 一定更正确。
  - 不要编造完整 ablation 收益。
fact_status: mixed
related_chunks: [KB-ENT-001, KB-ENT-003, KB-FACT-002]
---

---
chunk_id: KB-TECH-003
title: 工程追问集合
category: pressure
tags: [技术追问, vLLM, FSDP, Ray, sequence balancing, checkpoint, tool failure]
aliases: [系统面试追问, 分布式追问, 工具追问]
trigger_questions:
  - 面试官会怎么追问系统工程？
  - vLLM 和 FSDP 的显存怎么协调？
short_answer: |
  工程追问常见方向是：vLLM 为什么不能直接做 Agent、vLLM 和 FSDP 怎么分显存、Ray 和 Kubernetes/torchrun 的区别、sequence balancing 为什么重要、工具失败和超时怎么处理、checkpoint 能不能直接部署。回答要围绕状态机、显存生命周期、token 级负载均衡、工具降级和 FSDP 分片转换展开。
deep_answer: |
  vLLM 是推理引擎，不管理工具状态和反向传播；FSDP 负责训练分片和梯度同步；HybridEngine 在生成和更新之间切换资源。长序列 Agent 会让 KV cache 占用显存，`gpu_memory_utilization` 太高会 OOM，太低会牺牲吞吐。

  工具层面，要讲 timeout、retry、dedup、loop detection、call limit 和 metrics。checkpoint 层面，要讲 FSDP 分片不能直接部署，需要合并成 HF 格式，并验证 tokenizer 和 chat template。
follow_up_questions:
  - sequence balancing 为什么是 Agent RL 的难点？
  - Python 工具安全吗？
follow_up_answer_points:
  - 工具调用导致轨迹长度差异大，按样本均分会造成 GPU 等待。
  - 当前是子进程加 timeout，不是生产级安全沙箱。
pitfalls:
  - 不要只讲算法，不讲系统瓶颈。
  - 不要把工具安全和 checkpoint 部署说得过满。
fact_status: confirmed
related_chunks: [KB-DIST-002, KB-DIST-003, KB-AGENT-003]
---

---
chunk_id: KB-TECH-004
title: 数据评估追问集合
category: pressure
tags: [技术追问, 数据有效性, 评估可靠性, rule-based, 金融数据]
aliases: [数据追问, 评估追问, 金融真实性]
trigger_questions:
  - 生成数据会不会导致模板过拟合？
  - 评估可靠性如何保证？
short_answer: |
  数据追问要主动承认边界：生成数据适合 Phase 1 跑通 schema、reward 和训练闭环，但真实业务多样性不足，可能模板过拟合。评估方面，数值题 rule-based 容差相对可靠，概念题 F1 或关键词匹配有局限。最稳回答是用 held-out 模板、真实案例、公开数据、LLM-as-judge 和人工抽样逐步增强。
deep_answer: |
  如果面试官问为什么不用公开数据，回答不是“公开数据不好”，而是任务形式不完全匹配，需要补链式推理、difficulty、system prompt 和统一 schema。当前生成数据是可控起点，未来公开数据和真实财报是必要补充。

  如果问 77.6% 可靠性，要说明它来自当前评估集的统一口径，但还应补统计置信区间、错误类型分析和概念题 judge 校验。不要把自动评估说成专家审计。
follow_up_questions:
  - 怎么判断不是记忆模板？
  - rule-based 评估会误判吗？
follow_up_answer_points:
  - 按模板隔离测试、换参数、换表述、引入真实案例。
  - 会，尤其是概念题，同义表达和关键词堆砌都可能影响分数。
pitfalls:
  - 不要否认生成数据和自动评估的局限。
  - 不要把 77.6% 解释成生产金融能力。
fact_status: confirmed
related_chunks: [KB-FIN-005, KB-PRESS-002, KB-PRESS-003]
---

## 09 压力面问题

---
chunk_id: KB-PRESS-001
title: 被质疑只是复现
category: pressure
tags: [复现质疑, 个人贡献, 简历真实性, 压力面]
aliases: [是不是只是跑脚本, 创新在哪里, 去掉框架还剩什么]
trigger_questions:
  - 这是不是只是复现别人的项目？
  - 你自己的创新在哪里？
short_answer: |
  我会先承认底座不是从零造的，verl、Ray、vLLM、FSDP 和 PPO/GRPO 都是现有生态能力。但我的工作不是只跑脚本，而是把 Agent RL 的训练链路、工具调用稳定性、熵平衡机制配置、金融领域数据、reward schema 和三层评估体系串起来。框架提供训练能力，我做的是面向具体 Agent 和金融任务的适配、扩展、验证和问题分析。
deep_answer: |
  一个成熟回答要分层：算法上理解并接入 GRPO/PPO 和熵机制；工程上处理工具去重、循环检测、重试、监控和分布式训练配置；数据上构建金融 8 领域和 Parquet/JSONL schema；评估上设计综合、高难、领域专项并分析短板。

  如果继续被问“创新”，可以说创新不一定是提出全新理论，也可以是把算法放到真实 Agent 工具调用和金融垂直任务里跑通，解决数据格式、reward、训练稳定性和评估闭环问题。
follow_up_questions:
  - 有没有 ablation？
  - 你改了哪些模块？
follow_up_answer_points:
  - ablation 不完整就承认，并提出逐开关消融方案。
  - 模块按算法配置、Agent 工程、金融数据、评估体系讲，不讲行号。
pitfalls:
  - 不要和面试官争“这不是复现”，先承认底座再讲增量。
  - 不要把工程适配包装成理论原创。
fact_status: confirmed
related_chunks: [KB-SCOPE-001, KB-SCOPE-003]
---

---
chunk_id: KB-PRESS-002
title: 数据有效性质疑
category: pressure
tags: [数据有效性, 生成数据, 模板过拟合, 公开数据, 金融数据]
aliases: [生成数据靠谱吗, 会不会过拟合, 为什么不用真实数据]
trigger_questions:
  - 你自己生成的数据有效吗？
  - 会不会模型只学会模板？
short_answer: |
  这个质疑成立，所以我会把生成数据定位为 Phase 1：用可控数据先跑通训练和评估闭环。它的优势是 schema 统一、完整解答、难度可控、适合 rule-based reward；缺点是真实业务多样性不足，可能学到模板模式。后续应该混入公开金融数据、真实财报和中文金融市场数据，并保持 held-out 评估。
deep_answer: |
  对标准金融计算，模板化变体有价值，因为它能让模型反复学习 WACC、NPV、CAPM、久期等公式结构。对真实金融分析，仅靠模板不够，需要真实文本、表格、市场数据和开放式推理。

  因此合理口径是“当前数据保证训练可用和评估可控，但不是最终金融智能的全部数据来源”。这比简单说“数据很高质量”更经得住追问。
follow_up_questions:
  - 如何设计 held-out 测试？
  - 公开数据怎么导入？
follow_up_answer_points:
  - 按模板、题型、领域隔离，使用新参数和新表述。
  - 补推理链、标难度、统一 schema、去重和质量过滤。
pitfalls:
  - 不要否认生成数据局限。
  - 不要说 4239 条覆盖了金融全部场景。
fact_status: confirmed
related_chunks: [KB-FIN-001, KB-FIN-005]
---

---
chunk_id: KB-PRESS-003
title: 评估可靠性质疑
category: pressure
tags: [评估可靠性, rule-based, LLM-as-judge, FinBench, 指标]
aliases: [评估靠谱吗, rule-based误判, 77.6可信么]
trigger_questions:
  - 你的评估可靠吗？
  - rule-based 评估会不会误判？
short_answer: |
  当前评估可靠性是“计算题相对可靠，概念题有局限”。数值题可以用相对容差和公式结果校验，误判较少；概念题如果只用 F1 或关键点匹配，可能低估同义表达，也可能高估关键词堆砌。我会重点相信分层趋势：easy 高于 hard，计算型高于监管概念型；对概念题绝对准确率，要补 LLM-as-judge 和人工抽样校验。
deep_answer: |
  三层评估设计合理：综合评估看整体，高难基准看上限，领域专项看短板。但任何自动评估都有误差，尤其是金融监管、合规和开放分析题。

  如果正式做报告，应该补 bootstrap 置信区间、错误类型分析、人工抽样、judge rubric 和多评估器一致性。当前文档没有这些统计细节，所以面试里不能把 77.6% 说成无争议的生产级能力。
follow_up_questions:
  - 为什么不用 LLM-as-judge 作为主指标？
  - FinBench 45.5% 是失败吗？
follow_up_answer_points:
  - judge 有成本和偏差，适合作为概念题补充。
  - 45.5% 暴露高难短板，不是失败，而是优化方向。
pitfalls:
  - 不要把 rule-based 评估说成等同专家评审。
  - 不要只报总分，不讲题型差异和局限。
fact_status: confirmed
related_chunks: [KB-FIN-003, KB-FIN-004]
---

---
chunk_id: KB-PRESS-004
title: 不展示源码的压力面
category: pressure
tags: [源码不展示, 实现解释, 压力面, 技术可信度]
aliases: [面试官要看代码, 不给看源码, 怎么证明]
trigger_questions:
  - 如果我不展示源码，怎么讲清楚实现？
  - 面试官要求看代码怎么办？
short_answer: |
  我会说项目源码不方便展示，但可以把实现讲到模块和数据流层面：配置如何进入训练、数据如何从 Parquet 变成 DataProto、vLLM 如何生成、ToolAgent 如何暂停执行工具、reward 如何打分、GRPO 如何算 advantage、FSDP 如何更新、checkpoint 如何恢复和转部署。能讲清状态、输入输出和失败处理，比背行号更有说服力。
deep_answer: |
  面试官如果继续追问，可以用具体机制回答：ToolAgent 有 active 样本、call counter、done 状态、工具历史和 mask；Python 工具是 conda 子进程加 timeout；搜索工具有缓存和重试；熵优势是标准化 entropy 乘到 advantage；FSDP checkpoint 需要合并成 HF 格式才能部署。

  这种表达既不暴露源码，也能证明你知道系统怎么运行。不要用“保密”来挡所有技术问题，否则会显得没有真正做过。
follow_up_questions:
  - 可以画训练流程吗？
  - 能说出一个踩坑吗？
follow_up_answer_points:
  - 数据加载、rollout、reward、advantage、update、checkpoint 六步讲清。
  - 可讲 vLLM/FSDP 显存切换、工具超时、mask 错、dataloader resume 等。
pitfalls:
  - 不要只说“不能展示”而不解释。
  - 不要用源码行号替代系统理解。
fact_status: confirmed
related_chunks: [KB-SCOPE-003, KB-DIST-004, KB-AGENT-001]
---

---
chunk_id: KB-PRESS-005
title: 为什么不用 PPO
category: pressure
tags: [为什么不用PPO, GRPO, critic, 显存, outcome reward]
aliases: [PPO质疑, GRPO太粗糙, critic信用分配]
trigger_questions:
  - 为什么不用 PPO？
  - GRPO 不用 critic，信用分配怎么办？
short_answer: |
  不是不用 PPO，而是这个任务更适合 GRPO 作为主 estimator。工具调用任务的 reward 多是最终答案级，训练 critic 去估计每个中间状态价值成本高、噪声大，还会占用显存。GRPO 用同一 prompt 的多条 trajectory 做相对比较，能更低成本地优化 outcome reward，把显存留给更大的 rollout 和更长上下文。
deep_answer: |
  如果任务有密集 reward 或明确中间状态价值，比如每一步都有可验证反馈，critic 很有价值。但金融 QA、搜索问答和数学推理常常是最终答案对不对，critic 学到的 value 可能很噪。

  GRPO 的问题也要承认：依赖组内多采样和 reward 方差。如果同组样本都错或都对，优势信号会弱。因此需要足够 rollout、多样化采样、好的 reward，未来也可以用 PPO/GAE 做对照实验。
follow_up_questions:
  - 什么时候 PPO 更合适？
  - GRPO 如何处理稀疏 reward？
follow_up_answer_points:
  - 有密集过程反馈或状态价值明显时 PPO/critic 更合适。
  - 增加采样、多样性、过程 reward 或引入 critic 对照。
pitfalls:
  - 不要把 PPO 说成落后算法。
  - 不要说 GRPO 解决了全部信用分配问题。
fact_status: confirmed
related_chunks: [KB-RL-002, KB-RL-003]
---

---
chunk_id: KB-PRESS-006
title: 为什么需要熵
category: pressure
tags: [为什么需要熵, 高熵, 探索, 工具调用, 压力面]
aliases: [熵质疑, 高熵不是错误吗, 熵会乱探索吗]
trigger_questions:
  - 为什么需要熵，不直接用 reward 不行吗？
  - 高熵和高价值有什么关系？
short_answer: |
  只用 reward 也能训练，但 Agent 工具调用里的 reward 太粗，不能告诉模型哪些 token 或决策点最关键。熵提供的是“不确定性位置”的信号，帮助识别工具返回后、分支选择处、信息整合处这些值得关注的位置。熵不是正确性标签，也不是让模型无限随机，而是辅助分配采样预算和训练权重。
deep_answer: |
  面试官可能会说“高熵不就是模型没把握吗，为什么要放大？”回答要点是：高熵不是奖励本身，而是信息结构信号。工具结果进入上下文后，模型需要重新判断证据，这个位置的策略选择会影响最终答案；如果被普通模板 token 稀释，RL 学习效率会低。

  同时要强调约束：branch 上限、call limit、KL、clip、grad clip、去重和循环检测都在防止无效探索。
follow_up_questions:
  - 怎么防止过探索？
  - 熵机制有没有实验验证？
follow_up_answer_points:
  - 用工具限制、KL、clip、分支上限和失败降级控制。
  - 机制已接入，完整 ablation 仍需补充，不能硬编。
pitfalls:
  - 不要说高熵 token 一定更重要或更正确。
  - 不要说熵机制完全解决工具调用训练难题。
fact_status: mixed
related_chunks: [KB-ENT-001, KB-TECH-002]
---

---
chunk_id: KB-PRESS-007
title: 工具安全压力点
category: pressure
tags: [工具安全, Python sandbox, API key, 搜索工具, 失败降级]
aliases: [Python安全吗, 工具失败怎么办, API key]
trigger_questions:
  - Python 工具安全吗？
  - 搜索 API key 怎么保护？
short_answer: |
  当前项目更偏研究训练环境，不应该把工具安全夸成生产级。Python 工具是指定 conda 环境的子进程执行，有 timeout，但不是强隔离沙箱；搜索工具依赖外部 API，key 应通过环境变量或独立配置注入，不能硬编码。工具失败会影响 rollout 质量，所以项目用重试、缓存、错误返回、call limit 和监控做降级。
deep_answer: |
  生产级 Agent 需要更强安全措施：容器隔离、只读文件系统、网络限制、资源配额、审计日志、敏感信息脱敏和工具权限白名单。当前项目价值在训练研究闭环和工程稳定性，不是安全产品。

  面试中承认边界反而更专业。可以说：“我不会把 conda 子进程叫安全沙箱。如果上生产，我会把 PythonTool 放到独立容器或远程 sandbox，并限制文件和网络权限。”
follow_up_questions:
  - 工具返回恶意内容怎么办？
  - API 限流怎么处理？
follow_up_answer_points:
  - 工具结果做长度限制、格式约束和内容过滤。
  - 限流用指数退避、缓存、并发控制和调用预算。
pitfalls:
  - 不要说当前 PythonTool 已经完全安全。
  - 不要在面试中暴露任何密钥或真实配置。
fact_status: confirmed
related_chunks: [KB-AGENT-002, KB-AGENT-003, KB-AGENT-004]
---

## 10 高频检索索引

---
chunk_id: KB-IDX-001
title: 高频关键词索引
category: index
tags: [索引, 关键词, RAG检索, chunk map, 高频问题]
aliases: [怎么检索, 关键词映射, chunk索引]
trigger_questions:
  - 面试官问到某个关键词时检索哪些 chunk？
  - 如何快速定位知识卡片？
short_answer: |
  项目介绍检索 KB-OPEN；个人贡献和边界检索 KB-SCOPE；PPO、GRPO、SFT、KL、reward、mask 检索 KB-RL；entropy、AEARPO/ARAEPO、dynamic rollout、clipping 检索 KB-ENT；ToolAgent、搜索、Python、去重、循环检测、重试检索 KB-AGENT；Ray、vLLM、FSDP、DataProto、checkpoint、async 检索 KB-DIST；金融数据、schema、77.6%、FinBench 检索 KB-FIN；压力面检索 KB-PRESS 和 KB-TECH。
deep_answer: |
  关键词映射建议：

  PPO -> KB-RL-001；GRPO/critic -> KB-RL-002、KB-PRESS-005；outcome reward -> KB-RL-003；SFT -> KB-RL-004；mask/advantage -> KB-RL-005；KL -> KB-RL-006；熵/高熵 -> KB-ENT-001、KB-PRESS-006；AEARPO/ARAEPO -> KB-ENT-002；熵优势 -> KB-ENT-003；dynamic rollout -> KB-ENT-004；clipping -> KB-ENT-005；NaN/dual-clip -> KB-ENT-006。

  ToolAgent -> KB-AGENT-001；search/BrightData -> KB-AGENT-002；Python/sandbox -> KB-AGENT-003、KB-PRESS-007；去重/循环/重试 -> KB-AGENT-004；监控 -> KB-AGENT-005；Ray -> KB-DIST-001；vLLM/FSDP -> KB-DIST-002；sequence balancing -> KB-DIST-003；DataProto -> KB-DIST-004；checkpoint -> KB-DIST-005；async -> KB-DIST-006。

  finance_train/schema -> KB-FIN-002；金融 8 领域 -> KB-FIN-001；77.6/45.5/73.8 -> KB-FIN-003；监管和金融数学短板 -> KB-FIN-004；公开数据 -> KB-FIN-005；未来金融工具和 reward -> KB-FIN-006；事实冲突和待确认数字 -> KB-FACT-001、KB-FACT-002。
follow_up_questions:
  - 一个问题命中多个 chunk 怎么办？
  - 数字问题优先看哪里？
follow_up_answer_points:
  - 先用最直接 chunk 回答，再用 related_chunks 补机制。
  - 数字问题优先检索 KB-FACT-001 和 KB-FIN-003。
pitfalls:
  - 不要只靠向量相似度，数字和事实问题要精确匹配。
  - 压力问题必须参考 pitfalls，避免生成过度自信回答。
fact_status: confirmed
related_chunks: [KB-META-001, KB-FACT-001]
---

## 11 事实口径与不建议夸大的表述

---
chunk_id: KB-FACT-001
title: 已确认事实表
category: facts
tags: [已确认事实, 数据规模, 评估结果, 77.6, finance_train, FinBench]
aliases: [确认数字, 数据行数, 评估题数]
trigger_questions:
  - 哪些数字是确认的？
  - 金融数据和评估规模是多少？
short_answer: |
  已确认事实：项目主体路径是 `ae-ARPO/`；`finance_train.parquet` 为 3391 行 5 列，列为 `data_source`、`prompt`、`ability`、`reward_model`、`extra_info`；`finance_valid.parquet` 为 508 行；`train_10k.parquet` 为 10000 行；`hard_search_1k.parquet` 为 1071 行；金融评估为 340 + 200 + 8×60 = 1020 题。
deep_answer: |
  金融结果统一采用：finance 综合 77.6%，FinBench 高难 45.5%，8 领域专项平均 73.8%。难度拆分：easy 89.4%，medium 76.2%，hard 58.7%。领域拆分：宏观经济与政策 82.1%，财务报表分析 79.5%，公司金融与估值 77.8%，投资与组合管理 71.3%，微观经济学 70.5%，银行与货币市场 66.2%，金融数学 63.4%，金融监管与合规 59.8%。

  金融数据 8 领域样本量：宏观经济与政策 747，投资与组合管理 681，公司金融与估值 679，银行与货币市场 610，微观经济学 560，金融数学 374，财务报表分析 329，金融监管与合规 259，总计 4239 条 QA。
follow_up_questions:
  - 旧摘要低口径能不能说？
  - hard_search_1k 是 1000 条吗？
follow_up_answer_points:
  - 旧摘要低口径不采用，最终版统一为 77.6%。
  - hard_search_1k 实际是 1071 行，不要说成严格 1000。
pitfalls:
  - 不要把 4239 条说成训练集行数。
  - 不要把 finance_domains 8 个文件说成总共 60 题，它们是各 60 题。
fact_status: confirmed
related_chunks: [KB-META-002, KB-FIN-003]
---

---
chunk_id: KB-FACT-002
title: 待确认与不建议夸大
category: facts
tags: [待确认, 不夸大, GAIA, API调用降低, ablation, entropy clipping]
aliases: [不能主动说的数字, 风险口径, 夸大风险]
trigger_questions:
  - 哪些说法不能主动夸大？
  - 哪些事实需要标为待确认？
short_answer: |
  GAIA 61.2% Pass@5、工具调用频率降低约 50%、API 调用降低 15-30% 等说法只能标为待确认或经验口径，不能作为主动主结果夸大。完整 ablation、每个熵机制的独立收益、动态 rollout 的稳定提升也需要进一步实验支撑。Python 工具只能说子进程加 timeout，不能说生产级安全沙箱。
deep_answer: |
  熵相关口径也要谨慎：Entropy-Aware Advantage 是明确使用 token entropy 的机制，即用标准化 entropy 调整 advantage；但当前可见裁剪公式不应被说成“clip 上下界直接由 entropy 数值逐 token 决定”。更稳妥表达是：熵感知 advantage 与 policy update 稳定机制组合，用于控制训练行为和更新稳定性。

  未来方向包括 LLM-as-judge、实时行情搜索、pandas 财务建模、多轮金融工具任务、公开金融数据大规模导入、中文金融数据和金融专用 reward，这些不能写成已完成成果。
follow_up_questions:
  - 如果面试官问 ablation 怎么办？
  - 如果问 API 降低多少怎么办？
follow_up_answer_points:
  - 承认完整 ablation 还需补充，并说明消融设计。
  - 可以说去重和缓存能减少重复调用，但 15-30% 不是本次核对的硬结果。
pitfalls:
  - 不要为了简历好看编造未核实数字。
  - 不要把“支持/可配置”说成“已验证显著提升”。
fact_status: to_verify
related_chunks: [KB-TECH-002, KB-AGENT-004, KB-ENT-005]
---
