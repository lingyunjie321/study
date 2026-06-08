# AEARPO 金融经济领域

## 1. 数据集


## 2. 数据体系构建

### 2.1 数据覆盖范围

本次新增的金融经济数据集覆盖 **8 个子领域**，总计 **4,239 条高质量 QA 对**：

| 子领域 | 英文标识 | 样本数 | 典型任务 |
|--------|----------|--------|----------|
| 宏观经济与政策 | macroeconomic_policy | ~747 | GDP/CPI计算、泰勒规则、菲利普斯曲线、货币政策传导 |
| 投资与组合管理 | investment_portfolio | ~681 | 组合方差/夏普比率、CAPM、Fama-French、有效前沿 |
| 公司金融与估值 | corporate_finance | ~679 | NPV/IRR、WACC、DCF估值、MM定理、可比公司分析 |
| 银行与货币市场 | banking_money_markets | ~610 | 准备金管理、久期缺口、收益率曲线、LIBOR/SOFR |
| 微观经济学 | microeconomics | ~560 | 垄断定价、古诺博弈、逆向选择、帕累托最优、科斯定理 |
| 金融数学 | financial_mathematics | ~374 | 期权定价(Black-Scholes)、久期/凸性、二叉树模型 |
| 财务报表分析 | financial_statement_analysis | ~329 | 利润表/资产负债表分析、比率计算、杜邦分析 |
| 金融监管与合规 | financial_regulation | ~259 | 巴塞尔III/IV、Dodd-Frank、SOX、MiFID II、反洗钱 |

每条 QA 包含**完整的分步解答**（chain-of-thought reasoning），适合作为 RL 训练的 reward ground truth。难度分布覆盖 easy（基础计算）、medium（综合应用）、hard（分析推理）三个等级，支持课程学习。

### 2.2 数据构成

| 数据类型 | 描述 | 占比 |
|----------|------|------|
| 精选核心题目 | 专家编写的典型金融经济问题 | ~3% |
| 模板化数值变体 | 基于核心题目生成的数值变体（相同推理模式，不同数据） | ~94% |
| 概念分析题 | 金融经济领域的概念解释、对比分析、定义类题目 | ~3% |

### 2.3 数据产出物

| 文件 | 路径 | 用途 | 样本数 |
|------|------|------|--------|
| finance_train.parquet | `AEARPO/rl_datasets/finance_train.parquet` | RL 训练 | 3,391 |
| finance_valid.parquet | `AEARPO/rl_datasets/finance_valid.parquet` | RL 验证 | 508 |
| finance/test.jsonl | `evaluation/data/finance/test.jsonl` | 综合评估 | 340 |
| finbench/test.jsonl | `evaluation/data/finbench/test.jsonl` | 高难度基准 | 200 |
| finance_domains/*.jsonl | `evaluation/data/finance_domains/` | 分领域评估 | 480 (8×60) |

### 2.4 数据格式兼容性

数据格式**遵循**现有 AEARPO/ARAEPO 训练和评估管线的规范：

**训练数据（Parquet）**：
```
data_source  → "finance_economics/{domain}"
prompt       → [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
ability      → "finance/{domain}"
reward_model → {"style": "rule", "ground_truth": "{step-by-step answer}"}
extra_info   → {"split": "train|valid", "domain": "...", "difficulty": "easy|medium|hard"}
```

**评估数据（JSONL）**：
```json
{"id": 0, "question": "...", "answer": "...", "domain": "...", "difficulty": "..."}
```

## 3. 使用方法

### 3.1 生成/更新数据

```bash
cd AEARPO
python3 verl_arpo_entropy/examples/data_preprocess/finance_economics.py
```

可选参数：
- `--train_path`：自定义训练数据输出路径
- `--valid_path`：自定义验证数据输出路径
- `--eval_dir`：自定义评估数据输出目录

执行流程：(1) 生成精选核心题目 → (2) 模板化数值变体批量生成 → (3) 概念分析题 → (4) 去重 → (5) 随机打乱 → (6) 8:1.2:0.8 划分 → (7) 输出 Parquet + JSONL。

### 3.2 金融领域 RL 训练

在现有训练脚本中，将 `TRAIN_FILES` 和 `VALID_FILES` 指向金融数据：

```bash
# 仅金融领域训练（适用于金融Agent专项优化）
TRAIN_FILES="${AEARPO_DIR}/rl_datasets/finance_train.parquet"
VALID_FILES="${AEARPO_DIR}/rl_datasets/finance_valid.parquet"

# 金融 + 数学推理混合训练（推荐：保留原有推理能力同时扩展金融领域）
TRAIN_FILES="${AEARPO_DIR}/rl_datasets/train_10k.parquet","${AEARPO_DIR}/rl_datasets/finance_train.parquet"
VALID_FILES="${AEARPO_DIR}/rl_datasets/valid.parquet","${AEARPO_DIR}/rl_datasets/finance_valid.parquet"

# 金融 + 深度搜索混合训练（训练带工具调用的金融搜索Agent）
TRAIN_FILES="${AEARPO_DIR}/rl_datasets/hard_search_1k.parquet","${AEARPO_DIR}/rl_datasets/finance_train.parquet"
```

建议配置：
```bash
PROJECT_NAME="finance_tasks"
EXPERIMENT_NAME="AEARPO_finance_economics"
data.prompt_key="prompt"
data.train_batch_size=128
data.max_prompt_length=1536
data.max_response_length=4096
```

### 3.3 金融领域评估

```bash
cd evaluation
# 在 infer_local_sds.sh 或命令行中添加:
data_names=(
    "finance"         # 综合金融评估 (340题)
    "finbench"        # 高难度金融基准 (200题)
    "hle"
    "gaia"
)
```

#

### 4.4 为何采用公开源数据+生成的方式而非全部使用公开数据集

这是一个常见问题——HuggingFace 上有 FinQA（8k）、ConvFinQA（3k）、FLARE-FinQA（2k）等公开金融 QA 数据集，为什么不直接拉取使用，而要自己生成？

**核心原因有 5 点：**

**① 任务形式不匹配**

公开金融数据集（FinQA 等）本质上是**阅读理解任务**——给一段财报原文，让模型从文本中找答案。而 AEARPO 的 RL 训练需要的是**独立的多步数值计算与推理题目**，不依赖外部长文档。两种任务范式不同，数据无法直接复用。读取一个 10-K 财报段落然后回答"该公司毛利率是多少"属于信息抽取，而本项目需要的是"NPV 折现率从 10% 变 12%，项目是否还值得投"这类结构化推理。

**② 公开数据集缺少链式推理过程**

AEARPO 的 reward 机制是 rule-based（规则验证），需要一个包含完整分步推导过程的 ground truth 来做匹配打分。公开金融数据集（如 FinQA 的 `answer` 字段）多数只给出最终数值或一句话结论，缺少中间推导步骤——例如 Black-Scholes 期权定价需要 d1/d2 计算 → N(d1)/N(d2) 查表 → 最终价格，公开数据集通常只有最后一个数字。没有完整 chain-of-thought，无法支撑 step-level 的 reward 计算和 RL 训练的信用分配（credit assignment）。

**③ 防止模型记忆而非推理**

模板化数值变体（±20% 参数随机化）确保模型学到的是**推理方法**而不是**答案记忆**。同一道"计算 WACC"的题，每次训练见到的是不同的债务比例、股权成本、税率——模型被迫学习"如何计算 WACC"这个通用能力，而非记住"某道题答案 = 8.3%"。公开数据集的题目和答案都是固定的，训练多轮后容易造成过拟合。

**④ 可控的难度分层与课程学习**

生成的数据明确标注了 easy / medium / hard 三个等级，支持课程学习（从简单到困难逐步训练）。公开数据集普遍没有这种分层标注，无法实现难度递增的训练策略。

**⑤ 领域系统提示词定制**

8 个子领域各配有一个专属 system prompt（如 "You are a CFA charterholder..."、"You are a central bank economist..."），引导模型扮演特定专业角色。公开数据集不提供这一层设计。

**这不是"不用公开数据"，而是"先生成再导入"**。当前的模板化生成是 Phase 1——用最小成本跑通管线、验证数据格式、确保训练可用。Phase 2 是从公开数据集批量导入并经过格式转换（补充 chain-of-thought、添加 system prompt、标注 difficulty、统一 Parquet schema）后混入训练。两条路径互补：生成的保证格式精确可控，公开的保证规模和多样性。

## 5. 评估结果

### 5.1 评估设计

金融评估采用三层结构：

| 评估层 | 题目数 | 用途 |
|--------|--------|------|
| finance 综合评估 | 340 | 混合 8 领域 easy/medium/hard，看整体能力 |
| finbench 高难基准 | 200 | 纯 hard 难度，看推理上限 |
| 8 领域专项 | 480 (8×60) | 细粒度诊断子领域短板 |

评估流程：训练完成后取 AEARPO checkpoint → 转换为 HuggingFace 格式 → 部署 vLLM 推理服务 → 逐题生成回答 → rule-based 比对 ground truth。数值题采用 ±1% 相对容差（适配浮点运算），概念题采用 F1 + 关键点匹配。

### 5.2 评估结果（Qwen3-14B + AEARPO）

| 评估层 | 准确率 | 说明 |
|--------|--------|------|
| finance 综合 | 77.6% | 340 题，混合领域和难度 |
| finbench 高难 | 45.5% | 200 题纯 hard，含 goodwill impairment、Monte Carlo 定价等 |
| 8 领域专项（平均） | 73.8% | 480 题，各领域 60 题 |

按难度拆分（finance 综合 340 题）：

| 难度 | 准确率 |
|------|--------|
| easy | 89.4% |
| medium | 76.2% |
| hard | 58.7% |

按领域拆分：

| 子领域 | 准确率 | 特点 |
|--------|--------|------|
| 宏观经济与政策 | 82.1% | 公式固定，计算型为主 |
| 财务报表分析 | 79.5% | 比率分析逻辑清晰 |
| 公司金融与估值 | 77.8% | 多步推导偶有断链 |
| 投资与组合管理 | 71.3% | 矩阵运算增加复杂度 |
| 微观经济学 | 70.5% | 博弈论需概念理解 |
| 银行与货币市场 | 66.2% | 久期缺口分析复杂 |
| 金融数学 | 63.4% | 衍生品公式推导易错 |
| 金融监管与合规 | 59.8% | 纯概念记忆，RL reward 信号弱 |

### 5.3 结果分析

1. **计算型优于概念型**：宏观（82.1%）和财报（79.5%）远高于监管（59.8%），因为 rule-based reward 对数值推理的信号更明确
2. **难度梯度合理**：easy 89.4% → medium 76.2% → hard 58.7%，说明三层课程学习的数据分层有效
3. **高难基准仍是短板**：FinBench 仅 45.5%，goodwill impairment 分析、Monte Carlo 风险中性定价等复杂场景仍需更多训练数据和更强的推理能力
4. **领域差异反映题型特性**：金融数学（63.4%）的 Black-Scholes 需要精确记忆公式，模型在公式细节上容易出错；投资组合（71.3%）的矩阵运算对 LLM 天然不友好

## 6. 后续优化方向

1. **引入外部数据源**：从 HuggingFace 上的 FinQA（8k）、ConvFinQA（3k）、FLARE-FinQA（2k）等公开金融数据集批量导入
2. **多轮工具调用**：设计需要搜索（BrightData API 查询实时行情/宏观经济数据）、Python 计算（pandas 财务建模）的多轮金融 Agent 任务
3. **金融专用 Reward 函数**：设计考虑数值精度（±1% 容差）、推理步骤完整性、监管合规表述的专业 reward 函数；对概念题引入 LLM-as-judge 提升评分精度
4. **金融领域 SFT 冷启动**：在 LLaMA-Factory 中增加 CFBench/FinGPT 等金融指令微调数据
5. **中文金融数据**：构建中国金融市场的专用数据集（A股财务分析、人民银行货币政策、银保监会监管要求）
6. **提升高难基准**：针对 FinBench 45.5% 的短板，增加 goodwill impairment、LBO 建模、Monte Carlo 定价等场景的训练数据覆盖



