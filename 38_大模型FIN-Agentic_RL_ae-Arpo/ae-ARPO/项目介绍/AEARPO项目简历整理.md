# AEARPO 项目简历整理

> 关于简历：简历中的内容都是给参考的，你自己学了多少、学得多深，按自己需求写进简历即可。怎么方便面试怎么来，项目未必需要全部学会，实在来不及就把你学会的部分写进简历，灵活变通。

## 1. 项目概览

### 项目简介

AEARPO（Agentic Entropy-Balanced Reinforcement Optimization）是一个面向 LLM Agent 的强化学习训练框架。项目通过 token 级熵监测实现自适应分支采样和策略更新约束，解决 Agent 在多轮工具调用中因外部信息注入导致的高熵训练难题。

项目在 Qwen3-14B 上 GAIA 达到 61.2% Pass@5，在 QwQ-32B 上 GAIA 达到 53.4%、HLE 达到 12.8%。同时，项目将训练体系扩展至金融经济领域，构建了 4,239 条、覆盖 8 个子领域的 QA 训练数据和三层评估体系（1,020 题）。基于 AEARPO 训练的 Qwen3-14B 在金融综合评估上达到 67.6%，FinBench 高难度基准达到 45.5%，8 个领域专项平均 63.8%。

### 核心功能

- 自适应分支采样：token 级 entropy 监测，在高熵工具调用位置触发 `beam_size` 个推理分支，共享前缀以降低显存开销。
- 熵感知 Advantage 估计：高熵 token 的优势权重适度放大，低熵 token 的权重降低，让梯度在不同信息量的 token 间重新分配。
- 自适应裁剪上界：高熵位置获得更大的策略探索空间，同时避免裁剪范围剧烈波动。
- 多工具 Agent 支持：支持 Bing 搜索、Python 执行、多轮工具调用循环。
- Agent 工程改进：工具调用去重、循环检测、指数退避重试、状态一致性校验。
- 分布式训练：Ray + vLLM + FSDP2/Megatron-LM。
- 金融经济训练扩展：8 个子领域、4,239 条 QA、三层评估体系。

### 技术栈

| 类别 | 技术 |
| --- | --- |
| RL 框架 | verl（Volcano Engine RL） |
| 训练后端 | FSDP2 / Megatron-LM |
| 推理引擎 | vLLM 0.8+ / SGLang |
| 分布式 | Ray |
| SFT 框架 | LLaMA-Factory |
| 配置 | Hydra + OmegaConf |
| 实验追踪 | wandb + TensorBoard |
| 数据处理 | pandas / pyarrow / HuggingFace datasets |

## 2. 简历项目经历

### Python / AI 工程师版本

**2025.10-2026.04 | AEARPO Agentic RL 训练框架 | 核心开发**

**项目背景**

LLM Agent 在多轮工具调用场景中，搜索引擎和代码执行器返回的外部信息会注入高不确定性（entropy），导致标准 GRPO 训练中策略梯度被高熵 token 稀释；同时 Agent 容易在不确定时反复调用工具，形成低效循环。项目在 verl 框架基础上实现 AEARPO 算法，通过 rollout 阶段的熵感知分支采样和 update 阶段的熵平衡约束系统性地解决这一问题，并进一步完成金融经济领域训练扩展，以验证算法在专业推理场景下的有效性。

**主要负责**

1. 算法核心：实现 rollout 阶段 token 级 entropy 实时监测和自适应分支采样。vLLM 请求 top-10 logprobs，计算 Shannon entropy 并做 `log(vocab_size)` 归一化；通过 `P(branch) = random() - 0.5 * entropy_delta` 触发分支，共享前缀机制降低显存开销。
2. Policy Update：实现熵感知 Advantage 估计和自适应裁剪。`advantages *= (1 + 0.2 * entropy_normalized.detach())` 使高熵 token 权重放大至约 1.2x；`max_bound = (1 + epsilon) / ratio.detach() * ratio` 使高熵位置获得更大探索空间。核心代码位于 `core_algos.py` 的 `compute_policy_loss_entropy_balanced_clipping()`，约 110 行。
3. Agent 工程：完成工具调用去重、循环检测、指数退避、增强监控、状态校验五项改进。
4. 金融扩展：将训练体系从纯数学推理扩展到 8 个金融子领域，编写参数化数据生成管线，采用“核心题 + 模板化变体 + 概念分析题”的三层架构产出 4,239 条 QA。

**项目成果**

- Qwen3-14B：GAIA 61.2% Pass@5，HLE 24.0%。
- QwQ-32B：GAIA 53.4%。
- Agent 改进后，工具调用频率相比标准 GRPO 降低约 50%。
- 金融经济数据：8 个子领域，4,239 条训练 QA，1,020 道评估题。
- 金融评估：综合 67.6%，FinBench 高难 45.5%，领域专项平均 63.8%。
- 新增 11 项 Agent 监控指标，支持 TensorBoard 可视化。

### 金融 AI 方向版本

**2025.10-2026.04 | AEARPO 金融 Agent RL 训练 | 核心开发**

**项目背景**

通用大模型在金融经济推理上存在两个短板：一是缺乏结构化多步财务推理能力，例如 DCF 估值需要 6-8 步推导；二是在不确定时无法主动检索并验证外部数据。项目通过 RL 训练 Agent 的工具调用决策行为，使其学会在适当节点触发搜索或计算工具，并将训练体系扩展至金融经济领域，以强化该场景下的推理表现。

**主要负责**

1. 参与 AEARPO 熵平衡 RL 算法在金融数据上的训练适配。
2. 设计金融计算题的 rule-based reward。NPV、WACC、Black-Scholes 等题型涉及浮点运算，因此采用 ±1% 相对容差；`reward_model.ground_truth` 包含完整分步推导，用于 step-level 评分。
3. 按 CFA 知识框架拆分 8 个子领域：财务分析、宏观政策、公司金融、投资组合、银行货币市场、金融监管、微观经济学、金融数学。
4. 为每个领域定制角色化 system prompt，编写参数化数据生成管线，采用三层架构产出 4,239 条 QA。
5. 构建三层评估体系：finance 综合评估、FinBench 高难度基准、8 领域专项评估。

**项目成果**

- 金融经济训练数据 4,239 条，覆盖 8 个子领域。
- 三层评估体系 1,020 道题，覆盖 easy / medium / hard 三级难度和 8 个专业方向。
- 金融评估结果：综合 67.6%，FinBench 高难 45.5%，领域专项平均 63.8%。
- 模型在金融推理任务上具备多步计算和概念分析能力。

## 3. 面试话术参考

### 30 秒项目介绍

AEARPO 是一个面向 LLM Agent 的 RL 训练框架。核心创新是双阶段熵平衡：在 rollout 阶段通过 token 级 entropy 监测自适应启动分支采样，在 policy update 阶段通过熵感知 advantage 估计让高信息量 token 获得更大的学习权重，并通过自适应裁剪让高熵位置有更大的探索空间。

工程层面，我完成了 Agent 模块的多项改进，包括工具去重、循环检测、指数退避、监控指标和状态校验。为验证算法在专业场景下的有效性，我将训练体系扩展到金融经济领域，构建了 4,239 条 8 子领域训练数据和三层评估体系，训练后的模型在金融综合评估上达到 67.6%。

### 技术深度展示

工具调用任务的特殊之处在于，工具返回结果会向 LLM 的生成过程注入外部信息，这些位置的 token entropy 通常显著高于常规文本。高 entropy 意味着模型接收到了新信息，需要重点学习；低 entropy 则表示模型已经较确定，不需要大幅调整。

AEARPO / ARAEPO 在两个阶段处理这个问题：

1. Advantage 估计阶段：将 entropy 标准化后调整 advantage。高熵 token 的 advantage 被适度放大，低熵 token 的 advantage 被压低。
2. Policy Update 阶段：将标准 PPO 固定裁剪上界改成自适应上界，让高熵位置拥有更大的探索空间，同时通过 `.detach()` 避免梯度不稳定。

### Branch Sampling 技术细节

Rollout 阶段，vLLM 推理时实时请求 top-10 logprobs，计算 Shannon entropy 并做 `log(vocab_size)` 归一化。关键触发公式为：

```text
P(branch) = random() - 0.5 * (H_now - H_init)
```

当 entropy 相比初始状态增长时，分支触发概率提高。分支共享前缀，即高熵分歧点之前的 token 只生成一次，`beam_size` 个分支只从分歧点开始独立生成，相比 naive beam search 显著降低显存开销。

### Agent 工程改进亮点

Beam Branching 场景下，多个分支经常同时生成相同搜索查询。如果每个分支都独立调用 BrightData API，会造成明显浪费。项目设计了基于 `tag:content_hash` 的二级去重：

- 同批内通过 `seen_hashes` 字典查重。
- 跨步通过 `_dedup_cache` 缓存复用结果。
- `content_hash` 使用 `hash(content.strip().lower())` 标准化后计算。

这个去重只复用工具结果，不改变训练数据分布。

### 金融数据为什么是 8 个领域

划分依据是 CFA 知识体系的核心模块，并额外加入微观经济学和金融数学。原因是不同金融子领域的推理模式差异较大：

- 财务分析侧重 multi-step 比率计算。
- 公司金融侧重估值建模，例如 DCF / WACC / NPV。
- 金融数学侧重衍生品定价公式推导和参数敏感性分析。
- 监管类问题更偏概念记忆和法规复述。

### 遇到的最大挑战

最大挑战是自适应裁剪中的梯度稳定性。最初如果让 entropy 直接参与裁剪范围计算并回传梯度，训练中期容易出现 loss NaN。原因是高 entropy token 的 ratio 变化剧烈，裁剪范围跟着大幅波动，形成正反馈。

最终使用 `.detach()` 将裁剪范围变成纯前向调节器，让梯度只通过 ratio 和 advantage 本身回传，训练稳定性显著提升。

另一个挑战是金融 reward 设计。NPV、WACC、期权定价等题型存在浮点误差，如果要求精确匹配，大量正确答案会被误判。因此项目采用 ±1% 相对容差，超出容差才判 0 分。

## 4. 相关技术关键词

1. AEARPO / ARAEPO / Entropy-Balanced RL / Agentic RL
2. Entropy-Aware Advantage Estimation / Adaptive Clipping
3. Branch Sampling / Beam Branching / Entropy Monitoring
4. GRPO / PPO / RLHF / RLVR（RL with Verifiable Rewards）
5. Ray / vLLM / FSDP2 / Megatron-LM / 分布式训练
6. Tool Deduplication / Loop Detection / Exponential Backoff
7. Agent Observability / State Validation / Agent Metrics
8. Finance & Economics RL / FinBench / DCF / Black-Scholes
9. verl（Volcano Engine RL） / Hydra / wandb
10. Qwen3 / QwQ / Llama3.1 / HuggingFace

## 5. 技术面试知识库

### 5.1 训练双阶段：SFT 冷启动 + RL 微调

项目训练分两个阶段，默认都是全参数微调：

1. SFT 监督微调：使用 LLaMA-Factory 在 54K 条 agentic 数据上做全参数监督微调，作为 RL 冷启动。目标是先让模型学会“好的 Agent 行为”长什么样。
2. RL 微调：在 SFT 模型或 instruct 模型基础上，用 GRPO 做强化学习微调。模型自己生成多条轨迹，经过工具调用并拿到 reward 后更新策略。

面试追问：为什么 RL 前需要 SFT 冷启动？

答案：Instruct 模型通常被训练成“一次性回答”模式，而工具调用 Agent 需要多轮交互、分支采样和多次工具调用。SFT 先让模型习惯工具调用和多轮推理，RL 再优化“何时调、调什么、调完怎么办”。实验中冷启动后收敛速度可提升 2-3 倍。

### 5.2 PPO 算法核心思想

PPO（Proximal Policy Optimization）的核心思想是限制策略更新幅度，避免新策略偏离旧策略过远导致训练崩溃。常见做法是裁剪策略比率：

```text
r(theta) = pi_theta(a|s) / pi_old(a|s)
clip range = [1 - epsilon, 1 + epsilon]
```

GAE（Generalized Advantage Estimation）用于估计优势函数，控制偏差与方差权衡。PPO 是策略更新方式，GAE 是优势估计方式。GAE 通常需要 Value 模型，但 PPO 本身不一定必须依赖 Value 模型。

### 5.3 GRPO 算法与优势估计

GRPO（Group Relative Policy Optimization）不需要单独训练 Value 模型，而是通过同组样本的相对排名估计优势：

```text
advantage = (reward - group_mean) / group_std
```

GRPO 适合 outcome-level reward，也就是整个回复只有一个最终分数的任务。本项目的工具调用任务 reward 信号明确，因此采用 GRPO 可以省下 critic 的显存，把资源留给 vLLM 的 KV cache，提高 rollout 效率。

### 5.4 熵与策略多样性

Entropy 衡量策略随机性：

```text
H = -sum p(a|s) * log p(a|s)
```

高熵表示策略更不确定，低熵表示策略更确定。工具返回结果后往往会出现高熵 token，这些位置包含更多新信息，是训练时应重点学习的位置。

项目中的熵平衡主要体现在三处：

1. Entropy-Aware Advantage：高熵 token 优势权重适度放大。
2. Entropy Clipping-Balanced：高熵位置允许更大探索空间。
3. Dynamic Rollout：通过熵预监测和分支惩罚控制工具调用效率。

### 5.5 Ray 分布式架构

Ray 用于分布式协调，支持 GPU 感知、动态任务调度和容错。项目中常见概念包括：

- WorkerGroup：一组执行相同角色的 worker。
- ResourcePool：资源池，负责管理 GPU 等计算资源。
- Role：ActorRollout、Critic、RefPolicy 等不同角色。

Role 到 Worker 的映射大致如下：

| Role | 作用 |
| --- | --- |
| ActorRollout | 推理生成 + 策略训练 |
| Critic | 价值评估，PPO 模式下使用 |
| RefPolicy | 参考策略，用于 KL 散度计算 |

所有 Role 共享 GPU 池，并通过 FSDP 实现模型分片和梯度同步。

### 5.6 vLLM 与 FSDP 协同

vLLM 负责推理生成，FSDP 负责梯度更新。项目通过 `gpu_memory_utilization: 0.6` 控制 vLLM 的显存占用，剩余显存留给梯度、优化器状态和训练阶段中间变量。

verl 的 HybridEngine 在两个阶段之间做模型状态切换：

- 生成阶段：模型分片给 vLLM，用于 rollout 推理和 KV cache。
- 训练阶段：收回模型分片给 FSDP，用于反向传播和参数更新。

面试追问：vLLM 能否直接做 Agent？

答案：不能。vLLM 是无状态推理引擎，不能直接维护多轮交互和工具调用状态。ToolAgent 在 vLLM 基础上封装状态机逻辑，负责识别工具调用、执行工具、拼接结果并继续生成。

### 5.7 自适应裁剪机制

标准 PPO 使用固定裁剪范围 `[1 - epsilon, 1 + epsilon]`。ARAEPO 将上界改为动态计算：

```python
min_bound = torch.full_like(ratio, 1 - cliprange_low)
max_bound = (1 + cliprange_high) / ratio.detach() * ratio
pg_losses2 = -advantages * torch.clamp(ratio, min_bound, max_bound)
```

直观效果：

- `ratio > 1`：策略概率正在增加，上界更严格，避免过度偏向。
- `ratio < 1`：策略概率正在减少，上界更宽松，允许更多探索。
- `.detach()`：断开裁剪范围计算的梯度路径，避免梯度爆炸。

### 5.8 DataProto 数据协议

DataProto 是项目自定义的数据传输协议，包含：

- `batch`：TensorDict，保存 `input_ids`、`attention_mask`、`responses`、`old_log_probs`、`advantages` 等张量。
- `non_tensor_batch`：非张量字段，例如 `uid`。
- `meta_info`：额外元信息。

使用 TensorDict 的原因是它支持批量切片、concat、reorder 等操作，适合分布式训练中的数据分片。

### 5.9 Dual-Clip PPO

Dual-Clip PPO 在 advantage < 0 时增加额外裁剪，避免负优势被过度放大。

```python
pg_losses3 = -advantages * clip_ratio_c
clip_pg_losses2 = torch.min(pg_losses3, clip_pg_losses1)
pg_losses = torch.where(advantages < 0, clip_pg_losses2, pg_losses1)
```

作用：当模型当前策略比随机差时，限制策略继续变差的程度，防止低熵位置被过度调整。

### 5.10 多工具 Agent 与工具调用

Agent 使用 ReAct / Tool Calling 模式：模型生成工具调用请求，外部工具执行后返回结果，模型再基于结果继续生成。

ToolAgent 封装的核心接口：

- `reset()`：初始化状态。
- `step()`：执行一轮生成和工具调用。
- `get_final_responses()`：收集最终回复。

工具调用失败时，项目采用三级防护：

1. 指数退避重试：`delay = min(2^retry, 30s)`。
2. 循环检测熔断：连续多次调用同一工具且内容相似度过高时提前终止。
3. 去重缓存：复用历史工具结果，减少重复请求。

### 5.11 分布式训练中的序列均衡

序列均衡（Sequence Balancing）将数据按序列长度重新分片，确保每个 GPU 处理的总 token 数相近，避免部分 GPU 因样本过短或过长而空闲。

面试重点：RL 训练中不同 trajectory 长度差异很大，有的样本会多次调用工具，有的样本无需调用工具。如果不做序列均衡，GPU 负载会严重不均。

### 5.12 FSDP 模型分片策略

FSDP2 支持更细粒度的参数分片，适合 14B 及以下模型训练。对于 30B+ 模型，可切换到 Megatron-LM，结合 Tensor Parallel 和 Pipeline Parallel。

项目还支持 `use_remove_padding` 移除 padding token，减少无效计算。

面试追问：FSDP 和 DeepSpeed 的区别？

答案：FSDP 是 PyTorch 原生实现，与 `torch.compile` 和 vLLM 的兼容性更好。DeepSpeed ZeRO-3 在 hybrid engine 场景下可能出现额外显存管理问题。

### 5.13 训练流程与 Checkpoint

Checkpoint 保存内容：

- actor / critic 模型参数。
- dataloader 状态。
- global step。

恢复训练时，从 `latest_checkpointed_iteration.txt` 读取进度，并恢复 dataloader 状态，使训练从相同位置继续。

FSDP checkpoint 是分片格式，每个 rank 保存一部分参数，不能直接部署。部署前需要用 `convert_checkpoint_from_verl_to_hf_qwen3.sh` 合并为 HuggingFace 格式。

### 5.14 KL 散度与正则化

KL Penalty 用于防止策略偏离参考策略太远。项目支持自适应 KL 控制器，根据当前 KL 动态调整系数。

两种 KL 用法：

- in-reward KL：从 reward 中扣除，形式为 `reward = raw_reward - beta * KL`。
- KL loss：直接加入 loss，形式为 `loss += beta * KL`。

项目通过 `use_kl_in_reward` 开关控制是否在 reward 中加入 KL。

### 5.15 训练指标体系

| 指标 | 含义 | 正常范围 / 判断 |
| --- | --- | --- |
| `actor/pg_loss` | 策略梯度损失 | 应整体下降 |
| `actor/pg_clipfrac` | 被裁剪的策略梯度比例 | 0.1-0.3 较好 |
| `actor/ppo_kl` | 新旧策略 KL 散度 | 建议小于 0.05 |
| `actor/entropy` | 策略熵 | 缓慢下降，但不应过低 |
| `actor/grad_norm` | 梯度范数 | 小于 10 且为有限值 |
| `perf/tool_call_ratio` | 工具调用频率 | 相比 GRPO 降低约 50% |

判断训练是否正常：`pg_clipfrac` 过高说明更新幅度太大，需要降低学习率；entropy 逐渐下降但不能归零，否则意味着策略过度确定，失去探索能力。

### 5.16 配置管理（Hydra）

项目通过 YAML 文件定义配置，例如 `actor.yaml`、`agent.yaml`、`ppo_trainer.yaml`。训练时可以通过命令行 override 参数覆盖字段：

```bash
data.train_files=/path/to/finance_train.parquet
actor_rollout_ref.rollout.n=16
actor_rollout_ref.rollout.entropy_weight=0.2
```

Hydra / OmegaConf 支持分层配置和 merge，但训练中途修改配置通常需要重启。

### 5.17 Async Rollout 模式

Async Rollout 将推理和训练并行执行，提高 GPU 利用率。`AsyncLLMServerManager` 管理异步生成，Wake / Sleep 机制控制 vLLM 在训练和生成阶段之间切换。

对比：

- Sync：生成、训练、生成、训练串行执行，稳定但 GPU 空闲较多。
- Async：生成和训练并行，效率更高，但对数据依赖和同步处理要求更高。

### 5.18 模型支持（Qwen / Llama）

项目支持 Qwen2.5、Qwen3、Llama3.1 等模型。不同模型的 tokenizer 和 special token 处理不同：

- Qwen 系列使用特定 chat template。
- Llama 系列使用不同角色标记格式。

训练数据中的 prompt 格式必须与模型 chat template 匹配，否则角色标记偏移会影响推理质量。

### 5.19 Advantage 归一化

GRPO 中按 group 内均值和标准差归一化 advantage：

```text
advantage = (score - group_mean) / (group_std + epsilon)
```

归一化的原因是不同 prompt 的 reward 范围差异很大。归一化后，组间 reward 更可比，loss 优化更稳定。

### 5.20 梯度裁剪与稳定性

梯度裁剪用于防止梯度爆炸。项目中还会检查 `grad_norm` 是否为有限值：

```python
if not torch.isfinite(grad_norm):
    actor_optimizer.zero_grad()
else:
    actor_optimizer.step()
```

导致梯度不稳定的常见原因包括策略更新过大、ratio 极端值、数值不稳定。ARAEPO 的自适应裁剪和 `.detach()` 设计就是为了降低这类风险。

### 5.21 批处理与 Micro Batch

Dynamic Batch 按 token 数动态分批，而不是固定样本数。`ppo_max_token_len_per_gpu` 控制每张 GPU 最大 token 数。

优劣：

- Dynamic batch：更充分利用显存，长序列少放几条、短序列多放几条。
- 固定 batch：实现简单，但可能浪费显存。

Gradient Accumulation 用于把大 batch 拆成多个 micro batch，累积梯度后再更新参数。

### 5.22 金融经济评估体系与结果

金融评估采用三层结构：

| 评估层 | 题目数 | 准确率 | 说明 |
| --- | ---: | ---: | --- |
| finance 综合评估 | 340 | 67.6% / 77.6% | 混合 8 领域、3 难度；不同截图中出现两个版本数值，简历项目简介处为 67.6%，面试问答处为 77.6% |
| FinBench 高难基准 | 200 | 45.5% | 纯 hard 难度 |
| 8 领域专项 | 480 | 63.8% / 73.8% | 各领域 60 题；不同截图中出现两个版本数值 |

按难度拆分：

| 难度 | 准确率 |
| --- | ---: |
| easy | 89.4% |
| medium | 76.2% |
| hard | 58.7% |

按领域拆分：

| 子领域 | 准确率 | 分析 |
| --- | ---: | --- |
| 宏观经济与政策 | 82.1% | 公式固定，计算型为主 |
| 财务报表分析 | 79.5% | 比率分析、杜邦分析逻辑清晰 |
| 公司金融与估值 | 77.8% | NPV / WACC 多步推导，长链推理偶有断链 |
| 投资与组合管理 | 71.3% | 涉及 CAPM、有效前沿、矩阵运算 |
| 微观经济学 | 70.5% | 需要博弈论和福利经济学概念理解 |
| 银行与货币市场 | 66.2% | 久期缺口和收益率曲线分析较复杂 |
| 金融数学 | 63.4% | Black-Scholes、二叉树等公式推导容易出错 |
| 金融监管与合规 | 59.8% | 纯概念记忆较多，RL reward 信号弱 |

结果分析：计算密集型领域（宏观、财报）明显高于概念密集型领域（监管、银行）。原因是数值计算题的 rule-based reward 信号明确，模型更容易学到正确推理路径；概念题依赖文本匹配，reward 信号更弱。改进方向是对概念题引入 LLM-as-judge 做细粒度语义评分。

## 6. 高频面试问答

### Q1. 介绍一下这个项目？

这是一个基于强化学习的大模型 Agent 训练框架。我在 verl 框架基础上设计并实现了全链路熵平衡机制（AEARPO / ARAEPO），解决 Agent 在多轮工具调用中的训练难题：高熵工具返回结果会导致策略梯度被稀释。

通过熵感知优势估计和自适应裁剪机制，高熵 token 可以获得更大的优势权重，同时高熵位置可以进行更大胆的策略探索。在 Qwen3-14B 上 GAIA 达到 61.2% Pass@5，工具调用频率相比标准 GRPO 降低约 50%。同时，我将训练体系扩展至金融经济领域，构建了 4,239 条专业数据和三层评估体系。

### Q2. PPO 算法的核心思想是什么？

PPO 的核心思想是限制策略更新幅度，防止新策略偏离旧策略过远导致训练崩溃。它通过裁剪策略比率 `r(theta)`，让更新范围限制在 `[1 - epsilon, 1 + epsilon]` 内。

面试追问：PPO 为什么需要裁剪？

答案：为了防止策略大幅跳变导致训练崩溃。ARAEPO 的自适应裁剪在高熵位置允许更大探索空间，在低熵位置更保守。

### Q3. GRPO 和 PPO 的区别？本项目为什么选 GRPO？

PPO 通常需要训练 critic 网络估计 value function，额外占用显存。GRPO 不需要单独训练 Value 模型，而是通过同组样本的相对排名估计优势：

```text
advantage = (reward - group_mean) / group_std
```

本项目选择 GRPO，是因为工具调用任务的 reward 信号明确，适合 outcome-level reward。省下 critic 显存后，可以给 vLLM 更大的 KV cache，提升 rollout 效率。

### Q4. ARAEPO 的熵平衡三大机制是什么？

1. Dynamic Entropy-Balanced Rollout：熵预监测 + 分支惩罚，在 rollout 阶段控制工具调用频率。
2. Entropy-Aware Advantage Estimation：熵标准化后调整 advantage，高熵 token 获得更大优势权重。
3. Entropy Clipping-Balanced Mechanism：自适应裁剪范围，高熵位置允许更大策略探索空间。

三个机制分别作用在 rollout、advantage 计算和 policy update 三个阶段，形成全链路熵平衡。

### Q5. 熵感知优势估计怎么实现？为什么需要标准化？

实现逻辑：

```python
valid_entropy = entropy * response_mask.float()
entropy_mean = valid_entropy_flat.mean()
entropy_std = valid_entropy_flat.std()
entropy_normalized = (entropy - entropy_mean) / entropy_std
advantages = advantages * (1 + 0.2 * entropy_normalized.detach())
```

需要标准化，是因为不同模型、不同 batch 的 entropy 范围差异很大。标准化后变成均值 0、标准差 1 的分布，可以统一使用 0.2 这样的调整系数。`.detach()` 确保 entropy 只调节 advantage 的量级，不参与梯度回传。

### Q6. 自适应裁剪范围怎么计算？

核心计算：

```python
min_bound = torch.full_like(ratio, 1 - cliprange_low)
max_bound = (1 + cliprange_high) / ratio.detach() * ratio
pg_losses2 = -advantages * torch.clamp(ratio, min_bound, max_bound)
```

效果：

- `ratio > 1`：策略概率正在增加，上界更严格。
- `ratio < 1`：策略概率正在减少，上界更宽松。
- `.detach()`：避免 `max_bound` 的计算引入额外梯度路径。

### Q7. AEARPO 和 ARAEPO 的核心区别是什么？

AEARPO 主要在 rollout 阶段做熵平衡，通过 token 级 entropy 监测在高不确定性位置启动分支采样，减少不必要的工具调用。

ARAEPO 在此基础上增加了 policy update 阶段的熵平衡，包括熵感知优势估计和自适应裁剪。简单说，AEARPO 优化采样效率，ARAEPO 进一步优化更新稳定性。

### Q8. PPO / GRPO 训练为什么需要 SFT 冷启动？

Instruct 模型通常习惯“一次性回答”，而工具调用 Agent 需要多轮交互：思考、调用工具、查看结果、再思考，必要时继续调用工具。直接让 instruct 模型做多轮工具调用，它可能第一轮就结束对话。

项目用 54K agentic SFT 数据做微调，让模型先学会工具调用行为模式，RL 只需要继续优化“何时调、调什么、调完怎么办”。

### Q9. Ray 分布式架构怎么设计？

架构采用 Role-Worker 映射：

- `Role.ActorRollout`：Actor 推理 + 训练，包含 vLLM 生成和 FSDP 更新。
- `Role.Critic`：价值评估，PPO 模式下使用。
- `Role.RefPolicy`：参考策略，用于 KL 散度计算。

所有 Role 共享 GPU 池，通过 FSDP 做模型分片和梯度同步。Ray placement group 确保不同进程绑定到正确 GPU。

### Q10. vLLM 和 FSDP 如何协同？训练时显存怎么分配？

vLLM 负责推理生成，FSDP 负责梯度更新。通过 `gpu_memory_utilization: 0.6` 控制 vLLM 显存占用，剩余显存留给梯度存储和优化器状态。

verl HybridEngine 在生成阶段将模型分片给 vLLM，在训练阶段收回给 FSDP。核心价值是平滑切换生成和训练两个阶段，避免 OOM。

### Q11. 训练指标有哪些？怎么判断训练是否正常？

重点关注：

- `pg_clipfrac`：0.1-0.3 较好，过高说明更新幅度太大。
- `entropy`：应逐渐下降但不应归零。
- `grad_norm`：应为有限值，过大或 NaN 需要跳过更新。
- `ppo_kl`：新旧策略 KL 不应过高。

如果 `grad_norm` 不是有限值，本次更新应跳过：

```python
if not torch.isfinite(grad_norm):
    actor_optimizer.zero_grad()
else:
    actor_optimizer.step()
```

### Q12. Checkpoint 怎么保存和恢复？FSDP checkpoint 能直接部署吗？

Checkpoint 保存 actor / critic 模型参数和 dataloader 状态，路径通常为：

```text
default_local_dir/global_step_{step}/actor
```

恢复时从 `latest_checkpointed_iteration.txt` 读取进度。FSDP checkpoint 是分片格式，不能直接部署，需要先合并为 HuggingFace 格式，再用 vLLM 或 transformers 加载。

### Q13. Async Rollout 是什么？和 Sync 模式有什么区别？

Async Rollout 让推理和训练并行执行，由 `AsyncLLMServerManager` 管理异步生成。Wake / Sleep 机制用于控制 vLLM 在生成和训练阶段之间切换。

- Sync：生成、训练串行执行，更稳定。
- Async：生成和训练并行执行，GPU 利用率更高，但同步逻辑更复杂。

### Q14. 金融数据怎么保证符合项目格式规范？

项目数据按 Parquet schema 构造，包含 5 个必要列：

| 字段 | 含义 |
| --- | --- |
| `data_source` | 数据来源 |
| `prompt` | 角色对话列表 |
| `ability` | 能力标签 |
| `reward_model` | 包含 `ground_truth` 的字典 |
| `extra_info` | 元信息字典 |

训练时通过 `data.train_files` 指定 Parquet 路径；评估 JSONL 包含 `question` 和 `answer` 字段，与 `data_loader.py` 的读取逻辑一致。

### Q15. 金融数据的 8 个子领域怎么划分？

按 CFA 知识体系和金融推理类型划分为：

1. 财务分析
2. 宏观政策
3. 公司金融
4. 投资组合
5. 银行货币市场
6. 金融监管
7. 微观经济学
8. 金融数学

划分依据不是简单凑数，而是不同领域的推理模式不同：财务分析偏多步比率计算，公司金融偏估值建模，金融数学偏公式推导，监管类偏概念记忆。

### Q16. 金融评估为什么分三层？

三层评估各有侧重点：

- finance 综合评估：看整体水平。
- FinBench 高难基准：看复杂推理上限。
- 8 领域专项：诊断具体领域短板。

这种分层设计可以同时回答三个问题：整体表现怎么样、困难题上限在哪里、哪类知识最薄弱。

### Q17. 金融评估流程怎么跑？

评估流程：

1. 取 AEARPO 训练后的 Qwen3-14B checkpoint。
2. 用 `convert_checkpoint_from_verl_to_hf_qwen3.sh` 将 FSDP 分片合并为 HuggingFace 格式。
3. 部署 vLLM 推理服务。
4. 对 1,020 道评估题逐题推理，每道题使用对应领域 system prompt。
5. 将模型输出与 ground truth 做 rule-based 比对。
6. 按 domain 和 difficulty 聚合准确率。

发现：计算密集型领域明显优于概念密集型领域；easy / medium / hard 的难度梯度符合预期；FinBench 纯 hard 仍有明显提升空间。

### Q18. reward_model 为什么要包含完整解答，而不只是最终答案？

如果 reward 只判断最终数值对错，模型可能通过 reward hacking 记住答案，而不是学会推理过程。同时，过程部分正确但最终一步错误的答案会被直接判 0。

包含完整 step-by-step 解答后，可以按步骤给分。例如 WACC 计算有 4 步，模型做对 3 步但最后一步公式错了，应得到部分分数，而不是 0 分。过程奖励更有利于 RL 学到正确推理模式。

### Q19. 被质疑只是复现跑了一下项目，怎么回答？

可以从四个层面回答：

1. 算法层面：理解、适配并配置 ARAEPO 的熵平衡机制，在金融场景下调试熵权重、reward 容差和评估体系。
2. 数据层面：设计 8 领域分类体系，编写参数化数据生成管线，扩展 4,239 条 QA。
3. 评估层面：设计综合 / 高难 / 领域专项三层评估体系，并完成全流程评估分析。
4. 工程层面：完成工具去重、循环检测、指数退避、监控指标、状态校验五项 Agent 改进。

### Q20. 测完接口性能后，思考过如何优化吗？

当前瓶颈和优化方向：

1. 熵计算开销：每次 rollout 都计算 token 级 entropy，top-10 logprobs 请求有额外通信成本。可以考虑低成本近似熵估计。
2. 自适应超参数：熵权重 0.2 是手动调的，可以根据 KL 散度和 clipfrac 动态调整。
3. vLLM 显存争抢：训练和推理分离部署可以解决显存冲突，但会增加通信开销。
4. 金融概念题评分：当前文本匹配对监管类题目精度不足，可以引入 LLM-as-judge 做细粒度语义评分。

### Q22. 模型在哪些题型上表现最差？怎么改进？

表现最差的两类是金融监管和金融数学。金融监管主要是概念记忆和条文复述，rule-based reward 的文本匹配精度不够；金融数学涉及 Black-Scholes 等公式，模型容易在公式细节上出错。

改进方向：

- 监管题引入 LLM-as-judge，替代简单文本匹配。
- 金融数学增加训练数据占比和模板变体数量。
- 两类任务都可以在 SFT 阶段加入更多相关数据做冷启动。
