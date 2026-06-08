# ARAEPO - 完整项目文档

## 这是什么

ARAEPO（Agentic Entropy-Balanced Policy Optimization）是一个训练 LLM Agent 的强化学习算法。它解决的问题很具体：Agent 在调用搜索、执行代码这些工具时，工具返回的结果引入了很大的不确定性（高熵），导致 RL 训练的梯度信号被这些位置稀释掉。标准 GRPO 对所有 token 一视同仁，不管你是“模型自己生成的流畅文本”还是“搜索引擎吐回来的结构化数据”。

ARAEPO 的思路是在训练的三个阶段都考虑熵的影响：Rollout 时根据熵动态调整采样策略，算 Advantage 时给高熵位置更大权重，Policy Update 时给高熵位置更大的裁剪空间。

### 核心机制

#### 熵感知优势估计

在标准 GRPO 算完 advantage 之后，用每个 token 位置的熵做一次重加权：

```python
entropy_normalized = (entropy - mean) / std
advantages *= (1 + 0.2 * entropy_normalized.detach())
```

高熵 token 的 advantage 放大 1.2x，低熵 token 缩小 0.8x。`.detach()` 确保熵只调节 advantage 的量级，不参与梯度计算。

#### 自适应裁剪

标准 PPO 的 ratio 裁剪是 `[1-ε, 1+ε]`，ARAEPO 把上界改成自适应的：

```python
max_bound = (1 + ε) / ratio.detach() * ratio
```

`ratio > 1`（策略在增加某 token 的概率）时上界比标准 PPO 紧；`ratio < 1` 时松。本质是给高熵位置的策略变化更多自由度。

#### Dynamic Rollout

生成阶段做熵预监测，在生成前用额外的小采样估计当前步的熵水平，高熵时多分配采样预算。连续多步高熵则触发分支惩罚，避免过度探索。

### 训练流程

一次迭代分四步：

1. **Rollout**：`VLLMAgentRollout` 驱动 `ToolAgent.reset() -> step()` 循环。每步 vLLM 生成文本，检测到工具调用就执行后把结果拼回去，同时做 Beam Branching（从活跃轨迹 fork 新分支继续探索）。
2. **Reward**：对生成结果打分。Deep Research 任务用的是一套复合 reward（格式合法性 + 答案正确性），具体逻辑在 `verl/utils/reward_score/deep_research.py` 里。
3. **Advantage**：先做熵感知调整，再过 GRPO 组内归一化。相比标准 GRPO 多一步 `advantages *= (1 + 0.2 * entropy_norm)`。
4. **Policy Update**：用自适应裁剪范围替代标准 PPO 的固定范围，算 PPO loss、反向传播、优化器更新。

### 配置要点

ARAEPO 多了三个核心开关，在 `ppo_trainer_dr.yaml` 里控制。截图中的代码块右侧被截断，能完整识别出的字段如下：

```yaml
actor_rollout_ref:
  actor:
    enable_entropy_balanced_clipping: true
    enable_entropy_balanced_advantage: true
    # 第三个开关/参数在截图右侧未完整显示
```

这些开关默认关掉时，行为退化到 AEARPO（只有 Beam Branching，没有 Policy Update 的熵平衡）。

### Agent 模块优化

在开源 Agent 实现基础上做了五项工程优化，都是训练中实际踩坑后加的：

- 工具调用去重：Beam Branching 经常多个分支同时搜一样的东西，通过 `tag:content_hash` 去重，API 调用降 15-30%。
- 循环检测：Agent 有时候会反复搜同一个东西的变体，滑动窗口检测到就终止轨迹。
- 指数退避重试：API 限流时原版立即重试没用，改成 `2s -> 4s -> 8s` 递增。
- 增强监控：原版只能看调用次数，加了分支效率、工具多样性、轨迹健康度等 11 项新指标。
- 状态校验：7 个内部列表在分布式训练中容易不同步，加了一致性校验。

所有优化通过 `agent.yaml` 配置开关控制。详见 `Agent优化说明.md`。

### 怎么跑

```bash
conda create -n araepo python==3.10
conda activate araepo
cd ARAEPO && pip install -r requirements.txt

# 配好 API key 和模型路径后
cd ARAEPO/scripts
bash ARAEPO_Qwen3_14B_DeepResearch.sh
```

### 常见问题

**熵平衡效果不明显？**  
确认 `enable_entropy_balanced_clipping` 和 `enable_entropy_balanced_advantage` 都开了，检查 `entropy_weight` 是不是 0.2。

**训练 loss NaN？**  
一般是 `entropy_std` 为 0 导致除零。代码里已经加了：

```python
if entropy_std == 0:
    entropy_std = 1.0
```

要不就是 `cliprange_high` 设太大了，试试降到 0.1。

**Beam Branching 看起来没在有效探索？**  
看 TensorBoard 里的 `branch/active_ratio`，高的说明分支是从活跃轨迹 fork 的（正常），低的大概率是原轨迹走死了不停重启。

### 技术栈

PyTorch 2.6.0 / vLLM 0.6.3 / Ray / FSDP / Hydra / Qwen2.5、Qwen3、Llama3.1

### 核心文件速查

| 想知道什么 | 看哪个文件 |
| --- | --- |
| 熵平衡损失函数 | `verl/trainer/ppo/core_algos.py` |
| Actor 怎么用熵平衡 | `verl/workers/actor/dp_actor.py` |
| Agent 多轮交互 + Beam Branching | `verl/workers/agent/tool_agent.py` |
| 工具执行和重试 | `verl/workers/agent/tools/tool_executor.py` |
| Rollout 怎么驱动 Agent | `verl/workers/rollout/vllm_rollout/vllm_agent_rollout.py` |
| Deep Research reward | `verl/utils/reward_score/deep_research.py` |
| 训练脚本 | `ARAEPO/scripts/ARAEPO_Qwen3_14B_DeepResearch.sh` |
| Agent 配置（含优化开关） | `verl/workers/agent/agent.yaml` |

### 性能优化建议

| 瓶颈 | 当前方案 | 优化方向 | 优先级 |
| --- | --- | --- | --- |
| vLLM 推理速度 | 单节点 8 卡，TP=1 | 增大 TP size 或启用 chunked prefill | 中 |
| 工具调用延迟 | 同步串行执行 | 搜索缓存预热、异步批量请求 | 中 |
| FSDP 通信开销 | 全量梯度同步 | FSDP2 + `reshard_after_forward` | 低 |
| 训练显存紧张 | gradient checkpointing | LoRA 微调、activation offload | 高 |
| Beam Branching 冗余 | 随机分支 | 熵感知分支（根据当前步熵水平决定是否分支） | 中 |
| Agent 循环浪费 | 循环检测（已优化） | 基于 reward 信号的自适应提前终止 | 低 |

### 安全注意事项

- **API Key 保护**：BrightData API key 和 wandb key 不要在代码中硬编码，通过环境变量或独立配置文件注入，确保 `.gitignore` 包含这些敏感文件。
- **Python 代码执行隔离**：`PythonTool` 通过 conda 子进程执行用户代码，天然提供了一定隔离。但仍需注意超时控制（`timeout: 120`），防止恶意代码占用资源。
- **模型权重安全**：checkpoint 保存使用 FSDP 分片格式，加载时需验证模型来源可信。

### 如何扩展

**添加新工具**：在 `agent.yaml` 的 `tool_instances` 下注册新工具类（继承 `BaseTool`），实现 `trigger_tag` 和 `execute()` 方法即可，Agent 自动识别新工具。

**切换模型**：修改脚本中的 `ACTOR_MODEL_PATH` 和对应的 tokenizer 路径。框架已适配 Qwen2.5/Qwen3/Llama3.1，其他模型需在 `verl/models/` 下添加适配文件。

**换用 AEARPO 模式**：在 shell 脚本中将 `enable_entropy_balanced_clipping` 和 `enable_entropy_balanced_advantage` 设为 `False`，只保留 Beam Branching。

## 项目主体说明

### 核心功能

| 功能 | 说明 |
| --- | --- |
| 双算法支持 | AEARPO（自适应分支采样）+ ARAEPO（双阶段熵平衡） |
| 多模态 Agent 训练 | 支持 Search Tool / Python Tool / Sandbox 三种工具调用的 RL 训练 |
| 4.2K 金融经济数据集 | 8 个子领域的专业金融经济 QA，覆盖微观/宏观/公司金融/投资组合/银行/监管/财报分析/金融数学 |
| 高效推理引擎 | vLLM / SGLang 双引擎支持，训练时生成速度提升 3-5x |
| 灵活训练后端 | FSDP2 / Megatron-LM 可选，适配不同 GPU 规模 |

### 系统架构

```text
                  +----------------------------------+
                  |        Training Pipeline         |
                  |      (verl + Hydra config)       |
                  +----------------------------------+
                                  |
        +-------------------------+-------------------------+
        |                         |                         |
+---------------+        +------------------+        +----------------+
|   SFT Stage   |        |   RL Training    |        |   Evaluation   |
| (LLaMA-Factory)|       | (AEARPO/ARAEPO)  |        | (vLLM + Eval)  |
+---------------+        +------------------+        +----------------+
        |                         |                         |
        |              +----------+----------+              |
        |              |                     |              |
        |       +-------------+       +-------------+       |
        |       |   Rollout   |       |   Policy    |       |  Metrics
        |       |   (vLLM)    |       |   Update    |       | (pass@k)
        |       |   + Tools   |       | (FSDP/Mega) |       |
        |       +-------------+       +-------------+       |
        |              |
        |       +-------------+-------------+
        |       |   Search    |   Python    |
        |       |    Tool     |    Tool     |
        |       +-------------+-------------+
        |
        +---------------- Dataset Layer ----------------+
        |   Reasoning   |  DeepSearch  |    Finance     |
        |    10K QA     |    1K QA     |    4.2K QA     |
        +------------------------------------------------+
```

### Agent 编排图

```text
用户问题 -> [Rollout Engine]
                |
        +-------+-------+
        |       |       |
     [生成] [工具调用] [分支采样]
        |       |       |
        +-------+-------+
                |
        [熵监测] -> 高熵？ -> 增加分支 / 继续工具调用
                -> 低熵？ -> 结束当前轮次
                |
        [Reward 计算]
                |
        [Policy Update]
```

### 技术栈表

| 组件 | 技术 | 用途 |
| --- | --- | --- |
| RL 框架 | verl（Volcano Engine RL） | 训练编排、分布式管理 |
| 推理引擎 | vLLM 0.8+、SGLang | 训练时 rollout 加速 |
| 训练后端 | FSDP2、Megatron-LM | 分布式梯度计算 |
| 分布式 | Ray | 多节点多 GPU 调度 |
| SFT 框架 | LLaMA-Factory | 冷启动监督微调 |
| 配置管理 | Hydra/OmegaConf | YAML 配置覆盖 |
| 实验追踪 | wandb | 训练指标实时监控 |
| 数据处理 | pandas、pyarrow、datasets | Parquet/JSONL 读取 |
| 搜索 API | Bright Data（Bing） | Agent 工具调用 |
| 评估 | vLLM 推理 + 自定义评估器 | pass@k、准确率 |

## 核心组件详解

### 1. 熵平衡 Rollout 引擎

vLLM 推理时请求 top-10 logprobs，通过 `_calc_entropy()` 计算每个 token 的 Shannon entropy，并做 `log(vocab_size)` 归一化。归一化让不同词表大小的模型的 entropy 可比，例如 Qwen3-8B 词表 152064，Llama3.1-8B 词表 128256。

```text
输入：prompt + 工具配置
|
|-- 初始化采样 -> 生成 N 条初始轨迹（initial_rollouts=8）
|
|-- 熵值预监测 -> 对每条轨迹逐 token 计算 entropy
|   |-- entropy_delta = H_now - H_init > 阈值 -> 高熵位置
|   |-- entropy_delta <= 阈值 -> 继续常规生成
|
|-- 自适应分支采样（AEARPO 核心）
|   |-- P(branch) = random() - 0.5 * entropy_delta
|   |-- delta > 0（不确定在增长）-> 分支概率上升
|   |-- delta < 0（越来越确定）-> 分支概率下降
|   |-- 触发分支 -> 在高熵点启动 beam_size 个独立路径
|   |-- 前缀共享 -> 分歧点之前的所有 token 只生成一次
|   |-- 分支合并 -> reward 选最优 + entropy 标注保留
|
输出：N 条完整轨迹（含工具调用链 + token 级 entropy 张量）
```

关键配置及默认值：

- `rollout_n`：每组 prompt 最终保留的轨迹数（默认 16）
- `initial_rollouts`：首轮采样数（默认 8）
- `beam_size`：高熵点的分支数（默认 2）
- `entropy_weight`：熵权重系数（默认 0.2）
- `gpu_memory_utilization`：vLLM 占用显存比例（默认 0.6，剩余留给 FSDP）

### 2. Policy Update 引擎

ARAEPO 在标准 PPO loss 的基础上插入了两个熵感知操作，核心代码在 `core_algos.py:557-665` 的 `compute_policy_loss_entropy_balanced_clipping()` 函数（约 108 行）。

**Entropy-Aware Advantage Estimation：**

```python
entropy_normalized = (entropy - entropy_mean) / entropy_std  # 标准化
advantages = advantages * (1 + 0.2 * entropy_normalized.detach())
```

高熵 token（工具返回结果）优势权重放大至约 1.2x，低熵 token（固定格式文本）降至约 0.8x。标准化让不同 batch 的 entropy 可比，`.detach()` 确保熵只调节 advantage 量级，不参与梯度回传。

**Entropy-Balanced Clipping：**

```python
max_bound = (1 + cliprange_high) / ratio.detach() * ratio
```

`ratio > 1`（策略概率在增加）时 `max_bound < 1+ε`（更严格），`ratio < 1`（在减少）时 `max_bound > 1+ε`（更宽松）。`.detach()` 在这里同样关键，裁剪范围只做前向调节，断开梯度防止 NaN。

```text
输入：rollout 轨迹 + token 级 entropy + reward
|
|-- compute_grpo_outcome_advantage()
|      advantages = (reward - group_mean) / (group_std + 1e-8)
|
|-- Entropy-Aware Advantage（ARAEPO，可选开关）
|      advantages *= (1 + 0.2 * entropy_normalized.detach())
|
|-- Entropy-Balanced Clipping（ARAEPO，可选开关）
|      max_bound = (1 + ε) / ratio.detach() * ratio
|
|-- Dual-Clip PPO（防止 advantage < 0 时过度惩罚）
|      pg_losses3 = -advantages * clip_ratio_c  # c=3.0
|      pg_losses = min(pg_losses3, max(pg_losses1, pg_losses2))
|
|-- FSDP all-reduce -> optimizer.step() -> KL penalty
```

两个熵机制通过独立开关控制：`enable_entropy_balanced_advantage` 和 `enable_entropy_balanced_clipping`，方便逐个验证贡献。

### 3. 工具调用系统

三个工具均继承 `BaseTool` 基类：

| 工具 | 类路径 | 触发方式 | 返回格式 |
| --- | --- | --- | --- |
| `BingSearchTool` | `tools/search_tool.py` | `<search>query</search>` 标签 | 搜索结果摘要拼接 |
| `PythonTool` | `tools/python_tool.py` | `<python>code</python>` 标签 | stdout + stderr |
| `SandboxTool` | `tools/sandbox.py` | `<sandbox>code</sandbox>` 标签 | 执行结果 + 限制信息 |

`ToolAgent`（`tool_agent.py`）管理整个工具调用状态机。核心接口：`reset()` 初始化状态列表，`step()` 单步执行（生成文本 -> 检测标签 -> 执行工具 -> 拼接结果 -> 继续），`get_final_responses()` 收集最终输出。

7 个内部状态列表 `curr_inputs`、`init_inputs`、`result_masks`、`prompts_len`、`dones`、`call_counters`、`_tool_call_history` 追踪每个样本的工具调用进度。

Agent 工程改进（均通过 `agent.yaml` 控制开关）：

| 改进 | 位置 | 作用 |
| --- | --- | --- |
| 工具去重 | `tool_agent.py step()` | `tag:content_hash` 二级去重，同批复用结果 |
| 循环检测 | `tool_agent.py _detect_tool_loop()` | 连续同工具 + 高相似度则终止 |
| 指数退避 | `tool_executor.py _backoff_sleep()` | 429 限流时 `min(2^retry, 30s)` 退避 |
| 增强监控 | TensorBoard | 分支效率 + 工具多样性 + 轨迹健康度 11 项 |
| 状态校验 | `tool_agent.py _validate_reset_state()` | reset 后校验 7 个列表长度一致 |

### 4. 数据集层

| 数据集 | 来源 | 规模 | 用途 |
| --- | --- | --- | --- |
| AEARPO-Reasoning | 数学推理 + 多跳问答 | 10,000 条 | RL 训练主体 |
| AEARPO-DeepSearch | GAIA + WebDancer | 1,000 条 | 深度搜索训练 |
| AEARPO-FinanceEcon | 金融经济 8 领域 | 4,239 条 | 金融 Agent 训练（新增） |
| AEARPO-SFT | Agent 指令微调 | 54,000 条 | SFT 冷启动 |

## 训练双阶段

项目训练含两个阶段，均为全参数微调（FSDP 分片，不冻结层）：

```text
阶段一：SFT 冷启动（LLaMA-Factory）
数据：54K agentic SFT 数据
目标：让模型学会“多轮工具调用”的交互格式
代码：LLaMA-Factory/arpo_train_sft/
产出：SFT checkpoint 作为 RL 训练的初始化权重

阶段二：RL 微调（AEARPO/ARAEPO + verl）
数据：10K 推理 + 1K 深度搜索 + 4.2K 金融 = 15.2K RL 数据
目标：通过 reward 信号优化“何时调工具、调什么、调完怎么办”
代码：AEARPO/verl_arpo_entropy/verl/trainer/main_ppo.py
产出：最终 Agent checkpoint
```

SFT 和 RL 的分工：SFT 教模型“工具调用这件事可以做”，RL 教模型“工具调用这件事什么时候做、做几次、做完怎么办”。没有 SFT，RL 需要在巨大的搜索空间里先发现“调工具有时候有用”这一基本规律，收敛慢；没有 RL，SFT 模型只会模仿数据中的工具调用模式，不会根据 reward 自主调整策略。

如果显存放不下全参数微调，配置里支持切 LoRA，设 `lora_rank=32` 只训低秩适配器，其余权重冻结。

## RL 训练流程

```text
Step 1：数据加载
输入：train_10k.parquet（或 finance_train.parquet）
输出：prompt batch（batch_size=128）
逻辑：随机采样 -> tokenize -> padding -> 送入 vLLM

Step 2：Rollout（推理采样）
输入：prompt batch
处理：vLLM 生成 -> 工具调用检测 -> 执行工具 -> 继续生成
分支：entropy 监测，高熵点触发 beam_size 分支
输出：完整 trajectory + entropy 标注 + reward

Step 3：Advantage 计算
输入：reward + trajectory
处理：GRPO advantage = reward - baseline
      + entropy_aware 调整（ARAEPO）
输出：advantage tensor（seq_len x batch）

Step 4：Policy Update
输入：trajectory + log-prob + advantage
处理：compute ratio clip（AEARPO/ARAEPO 变体）
      PPO Loss -> backward -> FSDP all-reduce
输出：updated model weights
```

## 评估系统

### 评估数据集

| 基准 | 说明 | 指标 |
| --- | --- | --- |
| GAIA | 通用 AI 助手评估 | Pass@1、Pass@5 |
| HLE | Humanity's Last Exam | 准确率 |
| AIME24/25 | 数学竞赛 | 准确率 |
| MATH500 | 数学推理 | 准确率 |
| HotpotQA / 2Wiki / Musique | 多跳问答 | F1、EM |
| Finance | 金融经济综合（340 题） | 准确率 77.6% |
| FinBench | 金融高难度基准（200 题） | 准确率 45.5% |
| 8Domain 专项 | 金融子领域诊断（480 题） | 平均 73.8% |

### 评估流程

```text
启动 vLLM 推理服务 -> 加载模型 checkpoint

        [推理引擎]
        (vLLM Pool)
             |
    [数据加载] -> [工具执行] -> [答案解析]
             |
    [指标计算]（pass@k、F1、EM）
```

## 配置系统

训练通过 Hydra YAML 配置 + 命令行 override：

```yaml
# AEARPO/scripts/config/ppo_trainer.yaml
algorithm:
  adv_estimator: grpo
kl_ctrl:
  kl_coef: 0.6
```

## 性能数据

| 指标 | 数值 | 说明 |
| --- | --- | --- |
| GAIA（Pass@5） | 61.20% | Qwen3-14B AEARPO DeepSearch 配置 |
| HLE（Pass@5） | 24.00% | Qwen3-14B，同上 |
| 训练效率 vs GRPO | 约 50% 工具调用 | 熵平衡减少了不必要的搜索 |
| 14B 每步训练时间 | 约 10 min | 1 节点 8xH100，batch_size=12 |
| 金融数据集 | 4,239 QA | 8 子领域覆盖，可直接训练 |
| 金融综合评估 | 77.60% | Qwen3-14B + AEARPO，340 题 |
| 金融高难基准（FinBench） | 45.50% | hard，200 题 |
| 金融领域专项（平均） | 73.80% | 8 领域各 60 题 |
| 支持参数量级 | 3B-32B | Qwen2.5、Qwen3、Llama3.1 |

## 开发工作流

### 环境初始化

```bash
conda create -n aearpo python=3.10
conda activate aearpo
pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124
pip install flash-attn --no-build-isolation
cd AEARPO && pip install -r requirements.txt
```

### 快速验证

```bash
# 验证 verl 框架加载
python -c "from verl.trainer.main_ppo import main; print('verl OK')"

# 验证数据集格式
python -c "import pandas as pd; df=pd.read_parquet('AEARPO/rl_datasets/finance_train.parquet'); print(df.head())"
```

### 扩展新数据集

1. 编写数据预处理脚本放在 `examples/data_preprocess/`。
2. 确保输出 Parquet 包含：`data_source`、`prompt`、`ability`、`reward_model`、`extra_info`。
3. 在训练脚本中通过 `data.train_files` 指定新数据路径。

### 常见问题

**Q：OOM 怎么解决？**  
降低 `gpu_memory_utilization` 到 0.3-0.4，减少 `rollout_n` 和 `max_response_length`。

**Q：金融数据如何用于训练？评估结果如何？**  
在训练脚本中设置 `TRAIN_FILES=.../finance_train.parquet`，或与原推理数据混合训练以获得通用 + 金融双能力。基于 Qwen3-14B + AEARPO 训练后，金融综合评估（340 题）准确率 77.6%，FinBench 高难基准（200 题）45.5%，8 领域专项平均 73.8%。详细分析见 `FINANCE_ECONOMICS_OPTIMIZATION.md` 第 5 节。

**Q：工具调用一直失败？**  
检查 BrightData API key 和 network connectivity；确认 conda 路径在 `PythonTool` 配置中正确。

**Q：如何只用 4 卡训练？**  
设置 `rollout_n=8`、`initial_rollouts=4`、`beam_size=1`、`max_response_length=2048`。

## ARAEPO 训练流程细节（运行与排障补充）

本文讨论了 ARAEPO 训练流程的细节，包括环境搭建、数据处理、SFT 冷启动、RL 训练等多个方面，以及训练过程中可能遇到的问题。

只做参考，由于每个人择取的数据、超参数设置，还有各种乱七八糟的配置不同，所以实际训练过程都不一样。

### 环境搭建

硬件要求：8 张 A100（40GB）或 H100（80GB）。4 卡可以跑但需要调小 batch 和 rollout 参数，2 卡以下基本无法完整训练。

Flash Attention 的编译对机器内存要求较高，在内存不足的机器上可能编译失败。如果编译不过，可以用 `VLLM_ATTENTION_BACKEND=SDPA` 替代，但推理速度会下降。vLLM 和 PyTorch 的 CUDA 版本必须一致，两边都用 cu124 编译的版本。版本不匹配时会报 `undefined symbol`，错误信息不直接指向版本问题，需要检查 `pip list` 确认两边的 build tag。

Ray 在多次启动后可能残留进程。重新启动前需要执行 `ray stop --force` 清理，否则 `ray start --head` 会挂起而不报错。

verl 框架的加载路径有两套：`pip install -e .` 会把包注册到 site-packages，shell 脚本里还有 `export PYTHONPATH=.../verl_araepo_entropy`。如果两套路径指向不同位置，Python 会 import 到不同副本的同一模块，新添加的函数或类会在运行时找不到。排查方法是先 `pip uninstall verl` 再只靠 `PYTHONPATH` 加载，或者反过来，保持唯一路径。

### 数据处理

训练数据是 Parquet 格式。自定义数据时 schema 必须与 reward 函数期望的字段匹配，至少包含 `prompt` 列；如果 reward 函数依赖 `data_source` 字段也需要提供。字段缺失不会在数据加载阶段报错，而是在 reward 计算时因 key 不存在而 crash。

Ray 的 DataLoader 默认将全量数据读入内存再分发。对于 1k-10k 级别的数据集没有问题，但如果数据量到 10w 以上，需要改为流式加载或分片读取。

另外 prompt 需要按模型的 chat template 格式化后再输入。如果直接给裸文本，模型生成质量会明显下降。推荐用 tokenizer 的 `apply_chat_template` 方法处理。

### SFT 冷启动（可选）

如果走完整流程，先用 LLaMA-Factory 做监督微调。LLaMA-Factory 的配置链路比较长：`dataset_info.json` 定义数据集，YAML 配置引用数据集名，bash 脚本引用 YAML 路径。三层之间靠字符串匹配，任何一处拼写不一致都会导致加载失败。

数据格式需要转成 LLaMA-Factory 支持的格式（sharegpt 或 alpaca），字段名和结构必须严格对应。加载失败时的报错通常是泛化的 `data loading error`，不指明具体是哪个字段或哪条数据出问题，需要逐步打印中间变量定位。

### RL 训练

#### vLLM 推理是主要耗时环节

每次训练迭代分为两个阶段：vLLM 生成和 FSDP 梯度更新。生成阶段的耗时占比通常在 70% 以上。每张 GPU 需要同时推理几十条序列，每条最长 8K token，KV cache 占用显存的一半左右。`gpu_memory_utilization` 这个参数直接影响显存分配，设得太高会挤占 FSDP 的梯度存储空间导致 OOM，设得太低会降低 vLLM 的并发吞吐量。最优值没有通用公式，取决于具体的 batch size、序列长度和模型架构，需要根据实际 OOM 情况逐步下调。

#### Beam Branching 导致 batch 大小动态变化

配置中 `rollout_n=12`、`initial_rollouts=6`、`beam_size=2`，意味着每个 prompt 首先生成 6 条轨迹，然后在每一步从活跃轨迹 fork 新分支直到凑满 12 条。batch 大小在整个 step 中从 `N*6` 逐步增长到 `N*12`。如果某些轨迹提前生成 EOS 终止且无法 fork 出足够分支，该 sample 的最终 rollout 数可能不足 12。这会导致后续 GRPO 组内归一化时该组的样本数过少，标准差接近零，advantage 计算异常。

另一个问题是分支出来的轨迹，其 `old_log_prob` 是在分支后才计算的。如果分支时 `prompts_len` 等状态没有与新轨迹正确对齐，后续 loss 计算会使用错误的偏移量，表现是 loss 不 NaN 但训练不收敛。

#### 外部工具调用的延迟和可靠性

Bing 搜索 API 的响应延迟波动很大，同一批请求可能从几百毫秒到几十秒不等。`ThreadPoolExecutor` 的并发执行会被最慢的请求拖住整个 step。`timeout=120` 是兜底参数，但 120 秒对于一次训练 step 来说已经很长，实际训练中如果频繁触发超时，整体吞吐量会急剧下降。

Python 代码执行通过 `subprocess.run` 在 conda 环境中运行。如果模型生成了含死循环或大内存分配的代码，`subprocess.run(timeout=...)` 在某些情况下可能无法彻底终止子进程的子进程，导致 GPU 空转等待。

搜索 API 的配额也是实际训练中会遇到的问题。BrightData 免费额度有限，在 `rollout_n=12`、`train_batch_size=64` 的配置下，单个 epoch 可能产生上千次 API 调用。额度耗尽后 API 返回 403，训练中断。

#### 熵平衡在极端 batch 下的数值稳定性

ARAEPO 的熵感知优势估计依赖 `(entropy - mean) / std` 做标准化。当某个 batch 中熵分布极端，例如有一条超长序列几乎全部是高熵位置，标准化后的值整体偏移，导致 advantage 被过度缩放。表现是 loss 曲线出现周期性尖峰，幅度远超正常值但不触发 NaN，随后自动恢复。排查时容易被误判为数据异常或优化器问题，实际根因是标准化操作对极端分布敏感。

#### 显存管理的几个细节

FSDP 和 vLLM 共享 GPU 显存，每次迭代的显存状态切换顺序是：vLLM 推理（KV cache 占用）-> 释放 KV cache -> FSDP 加载完整模型权重 -> 前向 + 反向传播 -> 释放梯度和激活值 -> vLLM 推理（重新分配 KV cache）。如果某一环节没有完全释放，下一次迭代开始时显存不足会直接 OOM。Python GC 的回收时机不确定，可能需要手动调用 `torch.cuda.empty_cache()`，但脚本中没有在每步都执行。

`free_cache_engine=True` 参数控制在 rollout 结束后主动释放 vLLM 的 KV cache。默认值是 `False`，不开启的话每个 step 的 KV cache 残留会累积，大约 10 个 step 后显存耗尽。但部分 vLLM 版本在释放后重新初始化 cache engine 时有已知的报错，需要根据实际使用的 vLLM 版本测试确认。

#### FSDP checkpoint 的格式限制

FSDP 保存的 checkpoint 是分片格式，每张 GPU 各自保存自己持有的参数分片，因此 8 卡训练的 checkpoint 目录下有 8 个对应文件。加载时 GPU 数量必须与保存时一致：8 卡训练的 checkpoint 无法直接在 4 卡环境下加载，需要先执行 `merge_ckpt` 脚本将分片合并为完整模型权重，再在 4 卡上重新分片。

checkpoint 中除了模型参数还包含 `data.pt`，保存的是 dataloader 的迭代状态。如果训练中断后数据文件路径发生变化，或数据文件被重新排序，resume 后 dataloader 恢复的偏移量可能指向错误位置，导致部分样本被重复训练或被跳过。

### Agent 行为的可观测性

Agent 在一次 rollout 中执行多步工具调用、分支和终止，但训练日志默认只输出最终的 reward 和 loss。中间步骤的信息，例如模型生成了什么搜索 query、Python 代码是否执行成功、Beam Branching 的分支质量，在默认日志级别下不可见。

开启详细日志的问题在于数据量：12 个 rollout x 64 batch x 最多 10 个 step，日志总量很大。而且 vLLM 输出的是 token id 序列，需要 decode 为文本才能阅读，进一步增加计算开销。

默认的 AgentMetrics 只统计工具调用次数和成功率，无法判断 Beam Branching 的分支是否有效（是从活跃轨迹 fork 出来的，还是轨迹全部终止后从初始状态重启的），也无法判断 Agent 的搜索行为是否多样化。后续添加的增强监控：`branch/active_ratio`、`trajectory/loop_terminations`、`unique_queries`，可以在训练后通过 TensorBoard 回溯这些问题，但不是实时的。

### 评估与训练的差异

训练阶段的 reward 由 `verl/utils/reward_score/deep_research.py` 自动计算（格式校验 + 答案比对），而评估阶段在 `evaluation/src/evaluator.py` 中使用 LLM-as-Judge 方式评分。如果两种评分标准的一致性不够，可能出现训练 reward 高但评估质量低的情况。

训练时 vLLM 作为 Ray worker 的一部分启动，评估时需要单独启动 vLLM 推理服务。两者的参数配置（端口、模型路径、`max_model_len`）相互独立。训练时的 `max_model_len` 设为 prompt + response 总长（约 8192），评估时如果这个值设短了，长 prompt 会被截断，评估结果无效。

### 整体复杂度

这个项目涉及多个独立系统的协同：Ray 分布式调度、vLLM 推理引擎、FSDP 分布式训练、GRPO 强化学习算法、ToolAgent 多轮交互、外部工具调用。各模块之间的故障往往表现为下游模块的报错，而非真正根因所在模块。

例如搜索 API 超时导致 step 执行时间过长，最终报的是 Ray worker heartbeat timeout，排查方向容易被误导到 Ray 的网络配置而非工具调用的超时设置。
