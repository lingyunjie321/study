# RL 训练流程 代码追踪

## 概述

从命令行启动到 RL 训练完成，核心流程是：Hydra 加载配置 → 初始化 Ray + vLLM → 加载 Parquet 数据 → 循环执行 rollout（生成 + 工具调用）→ reward 计算 → policy update → 保存 checkpoint。以下追踪每个阶段的关键调用。

## 1. 入口与配置加载

### 调用链路

```
bash scripts/AEARPO_7B_Reasoning_1node.sh
  └─ python3 -m verl.trainer.main_ppo
       └─ verl/trainer/main_ppo.py:main()                          # L~50
            ├─ @hydra.main(config_path=CONFIG_PATH, config_name=CONFIG_NAME)
            │    └─ Hydra 从 ppo_trainer.yaml 加载默认配置
            │    └─ 命令行参数 override 配置文件中的对应字段
            ├─ ray.init()                                           # 启动 Ray 集群
            └─ TaskRunner.run()                                     # 训练主循环入口
```

### 关键代码

```python
# verl/trainer/main_ppo.py
@hydra.main(config_path=config_path, config_name=config_name, version_base=None)
def main(config):
    # Hydra 已将命令行参数合并到 config DictConfig 中
    ray.init(runtime_env={"env_vars": {"TOKENIZERS_PARALLELISM": "true"}})
    runner = TaskRunner.remote()   # 将 TaskRunner 部署为 Ray Actor
    ray.get(runner.run.remote(config))
```

## 2. 数据加载

### 调用链路

```
TaskRunner.run()
  └─ DataLoader.from_config(config.data)
       └─ verl/trainer/data_loader.py:from_config()                # L~30
            ├─ pd.read_parquet(train_files)                        # 列式读取
            ├─ tokenizer(prompt, max_length, padding)              # 批量 tokenize
            └─ 返回: IterableDataset (train + valid)
```

### 关键逻辑

训练脚本中的 `TRAIN_FILES` 和 `VALID_FILES` 是文件路径（支持逗号分隔的多文件），`prompt_key` 指定读取哪一列作为输入。金融数据同样使用 `prompt` 列作为输入。

## 3. Rollout 阶段

### 调用链路

```
TaskRunner.run() → rollout_engine.generate(prompts)
  └─ verl/workers/rollout/vllm_rollout/vllm_async_server.py        # L~200
       ├─ vLLM AsyncLLM.generate()                                  # 批量生成
       │    └─ 采样参数: temperature, top_p, max_tokens, beam_size
       ├─ 解析生成文本 → 检测工具调用标记
       │    └─ 若检测到 <tool_call> → ToolAgent.execute()
       │         └─ verl/workers/agent/tool_agent.py:execute()     # L~80
       │              ├─ 解析工具名 + 参数
       │              ├─ search_tool.search(query) → 返回结果
       │              ├─ python_tool.execute(code) → 返回输出
       │              └─ 将工具结果插入对话历史 → 继续生成
       │
       └─ 返回: 完整 trajectory (含工具调用链)
```

### AEARPO 分支采样关键代码

```python
# verl/workers/rollout/vllm_rollout/ (简化逻辑)
def generate_with_branching(prompt, beam_size, entropy_threshold):
    prefix_tokens = []
    while not done:
        logits = model.forward(prefix_tokens)
        probs = softmax(logits / temperature)
        entropy = -sum(probs * log(probs))        # token 级熵值

        if entropy > entropy_threshold:             # 高熵 → 分支
            branches = []
            for _ in range(beam_size):
                branch = generate_from(prefix_tokens, sample=True)
                branches.append(branch)
            # 选择 reward 最高的分支继续
            best = max(branches, key=lambda b: estimate_reward(b))
            prefix_tokens = best
        else:
            next_token = sample(probs)
            prefix_tokens.append(next_token)        # 低熵 → 常规采样
```

## 4. Reward 计算

### 调用链路

```
TaskRunner.run() → reward_manager.compute_reward(trajectories)
  └─ verl/utils/reward_score/deep_research.py:compute_score()      # L~10
       ├─ 解析 trajectory 的最终答案
       ├─ 与 reward_model["ground_truth"] 比对
       │    ├─ 数值题: 容忍度 ±1% 视作正确
       │    ├─ 多选题: 精确匹配选项字母
       │    └─ 开放式: LLM judge 评分 (可选)
       └─ 返回: float score ∈ [0, 1]
```

### 金融数据的 reward 计算

金融数据在 `reward_model.ground_truth` 中存储的是完整分步推导过程。当前 `compute_score` 做最终答案比对。未来可以扩展为按步骤给分——匹配到某步的中间值就加该步的分数。

## 5. Policy Update

### 调用链路

```
TaskRunner.run() → actor.update_policy(trajectories, rewards)
  └─ verl/workers/actor/dp_actor.py:update_policy()                # L~100
       ├─ 计算 old_log_prob (从 rollout 阶段缓存)
       ├─ 计算 new_log_prob (当前模型重新 forward)
       ├─ ratio = exp(new_log_prob - old_log_prob)
       ├─ ARAEPO Entropy Clipping (可选):
       │    └─ 若 token entropy > 阈值:
       │         ratio = ratio.detach()  # stop-gradient
       │         ratio = ratio * rescale_factor
       ├─ GRPO loss = -min(ratio * advantage, clip(ratio) * advantage)
       ├─ loss.backward()
       └─ FSDP all-reduce → optimizer.step()
```

## 错误恢复流程

```
生成超时
  └─ vLLM 客户端设置 timeout=120s
       ├─ 超时 → 重试 3 次 (exponential backoff)
       └─ 3 次后仍失败 → 跳过本条数据，log warning

工具调用失败
  └─ ToolAgent.execute()
       ├─ 网络错误 → 重试 (retry_count=3)
       ├─ Python 执行异常 → 返回错误信息给 LLM 继续推理
       └─ 工具未注册 → 降级为纯文本生成

显存不足
  └─ vLLM AsyncLLM.generate()
       └─ OOM → 自动降低 max_tokens (vLLM 内置机制)
```

## 关键代码片段汇总

1. **数据加载** — `verl/trainer/data_loader.py:30` — 从 Parquet 读取 prompt 列并 tokenize
2. **Rollout 生成** — `verl/workers/rollout/vllm_rollout/` — vLLM 批量推理 + 工具调用
3. **工具 Agent** — `verl/workers/agent/tool_agent.py:80` — 解析工具调用指令并执行
4. **Reward 计算** — `verl/utils/reward_score/deep_research.py:10` — 答案比对与打分
5. **Policy Update** — `verl/workers/actor/dp_actor.py:100` — GRPO loss + FSDP 同步
6. **金融数据生成** — `examples/data_preprocess/finance_economics.py` — 三层数据架构生成脚本
7. **评估加载** — `evaluation/src/data_loader.py:15` — JSONL 读取 + 领域分发
8. **评估指标** — `evaluation/src/metrics.py` — pass@k, F1, EM 计算
