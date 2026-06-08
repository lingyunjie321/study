# RL 训练流程 完整分析

## 概述

AEARPO 的 RL 训练流程核心机制是「生成时在高熵点分支采样，更新时对高熵 token 做约束」。这个流程解决了两个问题：(1) 标准 GRPO 在工具调用场景下产生大量低效调用——Agent 不确定时倾向于反复调用搜索来确认，浪费推理算力；(2) PPO 的 uniform clipping 对高不确定性的 token 和低不确定性的 token 一视同仁，导致高熵位置更新过激。金融经济数据扩展基于同一套数据 schema，通过命令行参数指定数据集路径即可接入。

## 完整生命周期

```
┌─────────────────────────────────────────────────────────────────────┐
│ 阶段 0: 环境初始化                                                  │
│   ┌─────────┐    ┌──────────┐    ┌───────────┐                     │
│   │ Hydra   │───▶│  Ray     │───▶│  vLLM     │                     │
│   │ Config  │    │  Cluster │    │  Workers  │                     │
│   └─────────┘    └──────────┘    └───────────┘                     │
├─────────────────────────────────────────────────────────────────────┤
│ 阶段 1: 数据加载 (每个 epoch 开始时)                                 │
│   finance_train.parquet (或 train_10k.parquet 混合)                 │
│     → pd.read_parquet → 读取 prompt 列                              │
│     → tokenizer(prompt, max_length=1536, padding=True)             │
│     → DataLoader (Iterable, batch_size=128)                        │
├─────────────────────────────────────────────────────────────────────┤
│ 阶段 2: Rollout (数据流的核心，占 70-80% 时间)                       │
│   ┌──────────────────────────────────────────────────────┐         │
│   │ prompt batch 进入 vLLM                                │         │
│   │   → vLLM.generate(temperature, top_p, max_tokens)     │         │
│   │   → 检测到 <tool_call>search("...")</tool_call>       │         │
│   │       → BrightData API 调用                           │         │
│   │       → 结果插入对话历史                               │         │
│   │       → 继续生成 (重复最多 call_limit=3 轮)           │         │
│   │   → token 级 entropy 计算                             │         │
│   │       → entropy > 阈值 → beam_size 分支 (AEARPO)      │         │
│   │   → 输出: trajectory + log_prob + entropy_info        │         │
│   └──────────────────────────────────────────────────────┘         │
├─────────────────────────────────────────────────────────────────────┤
│ 阶段 3: Reward 计算                                                 │
│   trajectory.final_answer vs reward_model["ground_truth"]          │
│     → 数值: |pred - gt| / |gt| < 1% → 1.0, else 0.0               │
│     → 选择: pred == gt → 1.0, else 0.0                             │
│   → reward tensor (batch_size,)                                    │
├─────────────────────────────────────────────────────────────────────┤
│ 阶段 4: Advantage 计算                                              │
│   GRPO: A_i = (r_i - mean(r)) / std(r)  (组内标准化)               │
│   ARAEPO 变体: A_i = A_i * entropy_weight_i                        │
│     (高熵 token 的 advantage 获得更大权重)                           │
├─────────────────────────────────────────────────────────────────────┤
│ 阶段 5: Policy Update                                               │
│   ratio = exp(log_prob_new - log_prob_old)                         │
│   loss = -min(ratio * A, clip(ratio, 1-ε, 1+ε) * A)  (PPO clip)  │
│   ARAEPO: 对高熵 token 在 clip 前做 stop-gradient                   │
│   → loss.backward() → FSDP all-reduce → optimizer.step()           │
├─────────────────────────────────────────────────────────────────────┤
│ 阶段 6: Checkpoint & Logging                                        │
│   → 保存 FSDP sharded checkpoint                                   │
│   → wandb.log(loss, reward, entropy, branch_ratio, ...)            │
│   → 可选: 转 HuggingFace 格式 (merge_ckpt/)                         │
└─────────────────────────────────────────────────────────────────────┘
```

## 关键数据结构

```python
# 训练数据 schema (Parquet 一行)
{
    "data_source": "finance_economics/corporate_finance",
    "prompt": [
        {"role": "system", "content": "You are a corporate finance expert..."},
        {"role": "user", "content": "Calculate WACC for..."}
    ],
    "ability": "finance/corporate_finance",
    "reward_model": {
        "style": "rule",
        "ground_truth": "Step-by-step answer with intermediate values..."
    },
    "extra_info": {
        "split": "train",
        "index": 0,
        "domain": "corporate_finance",
        "difficulty": "medium",
        "tools_required": []     # [] / ["search"] / ["python"]
    }
}

# 评估数据 schema (JSONL 一行)
{
    "id": 0,
    "question": "Calculate the NPV of a project with...",
    "answer": "Step-by-step: NPV = -500K + 150K * 3.7908 = $68,620",
    "domain": "corporate_finance",
    "difficulty": "medium"
}
```

## 完整执行示例（金融数据训练）

**输入 prompt**:
```
System: You are a corporate finance expert. Evaluate investments...
User: A project requires $800K initial investment, generates $220K/yr for 5 years. Discount 12%. NPV? Accept?
```

**Rollout 生成（vLLM）**:
```
Step 1: "Let me calculate the present value of the cash flows."
Step 2: "PV factor for 5 years at 12% = (1 - 1.12^-5) / 0.12"
Step 3: "= (1 - 0.5674) / 0.12 = 0.4326 / 0.12 = 3.605"
Step 4: "PV of cash flows = $220K * 3.605 = $793,100"
Step 5: "NPV = -$800K + $793,100 = -$6,900"
Step 6: "Since NPV is negative, the project should be rejected."
```

**Reward 比对**:
```
ground_truth 期望: NPV = -800 + 220 * 3.6048 = -800 + 793.05 = -6,950
模型输出: NPV = -6,900
误差 = |6900-6950|/6950 = 0.72% < 1% → reward = 1.0
```

## 关键设计模式

| 模式 | 应用 | 优势 |
|------|------|------|
| **策略模式** | `reward_manager` 可切换 naive/prime/custom | 不同任务用不同 reward 函数 |
| **模板方法** | `main_ppo.py` 定义训练循环骨架，具体实现交给 `rollout/actor/reward` | 核心流程固定，组件可替换 |
| **适配器** | `data_loader.py` 的 if-elif-else 分支处理不同数据集格式 | 新增数据格式只需加一个 elif 分支 |
| **观察者** | wandb callback 监听 loss/reward/entropy 变化 | 解耦训练逻辑和监控逻辑 |
| **工厂方法** | `ToolAgent` 根据 YAML 配置动态创建 search/python/sandbox 工具实例 | 通过配置文件新增工具 |

## 常见问题排查

**Q: 训练 loss 突然变成 NaN？**
排查顺序: (1) 检查 entropy_std 是否为 0 → 代码有兜底 `if entropy_std == 0: entropy_std = 1.0`；(2) 降 `clip_ratio_high` 从 0.3 到 0.1；(3) 降 `entropy_weight` 从 0.2 到 0.1；(4) 检查 tokenizer 是否和模型匹配。

**Q: 金融数据训练后模型在数学题上退化？**
混合训练时关注两个验证集的 reward 曲线——如果金融 reward 在涨但数学 reward 在跌，降低金融数据的采样比例（命令行指定 `data.train_batch_size` 分拆）。理想情况下混合训练应该让两个能力都上升或至少数学不退化。

**Q: 评估时金融数据被 data_loader 读取报错？**
确认 JSONL 文件在 `evaluation/data/{dataset_name}/test.jsonl` 路径下，确认每行 JSON 包含 `question` 和 `answer` 字段。`data_loader.py` 的 else 分支用这两个字段读取，不需要其他字段。
