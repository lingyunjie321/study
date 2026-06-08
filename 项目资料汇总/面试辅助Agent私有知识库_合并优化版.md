# 面试辅助 Agent 私有知识库：合并优化版

## 0. 使用说明与检索规则

本知识库包含两个项目，所有回答必须先判断 `project_id`，再组织面试回答。

- `project_id: DATA_ENGINEER_AGENT`：企业级 data_engineer agent 工程，也可称为企业级数据工程 Agent、Data Engineer Agent、企业数据智能 Agent、NL2SQL Agent、AI Harness / Runtime 平台。
- `project_id: FIN_AGENTIC_RL_ARPO`：大模型 FIN-Agentic_RL_ae-Arpo 工程，也可称为 FIN-Agentic RL、ae-ARPO、AEARPO / ARAEPO、Agentic RL 训练与评估平台、金融经济 Agent RL 项目。

### 0.1 强制路由规则

- 如果问题中出现 `data_engineer`、`企业级`、`数据工程`、`NL2SQL`、`SQL`、`Schema Linking`、`数据管道`、`ETL`、`调度`、`数据质量`、`指标口径`、`表字段`、`LanceDB`、`SQLGlot`、`MCP`、`Skills`、`Agent Harness`、`Workflow / Node` 等关键词，优先匹配 `DATA_ENGINEER_AGENT`。
- 如果问题中出现 `FIN`、`金融`、`大模型`、`Agentic RL`、`ARPO`、`AEARPO`、`ARAEPO`、`GRPO`、`PPO`、`强化学习`、`策略优化`、`熵`、`ToolAgent`、`Ray`、`vLLM`、`FSDP`、`FinBench`、`finance_train`、`77.6%` 等关键词，优先匹配 `FIN_AGENTIC_RL_ARPO`。
- 如果问题只说“Agent 项目”“RAG 项目”“工具调用项目”，不能直接混合两个项目。先根据上下文判断；仍无法判断时，先追问：“您想问的是企业数据工程 NL2SQL Agent，还是金融 Agentic RL 训练项目？”
- 如果检索结果来自两个项目，必须按问题关键词重新排序，只使用同一 `project_id` 的知识块回答。不要把两个项目的技术方案拼接成一个项目。

### 0.2 本合并版的切块建议

- 建议按二级标题和三级标题切块。每个知识块均显式出现 `project_id`，用于降低跨项目误召回。
- 检索时优先使用每个项目的“检索标签”“排除关键词”“口语化回答模板”“难点与解决方案”“风险点、边界与可改进方向”。
- 数字和结果类问题优先检索“事实口径”“风险点”“原始来源映射”，避免使用旧口径或待确认口径。

### 0.3 文件来源识别摘要

目录实际发现 6 个 Markdown 文件。合并正文主要来自 4 份项目知识库文件，2 份简历文件用于补充项目命名、技术栈和职责边界。

| 文件 | 来源判断 | 项目归属 | 主要内容 | 本合并版使用方式 |
|---|---|---|---|---|
| `企业级数据工程 Agent_claudecode整理版.md` | Claude Code 整理版 | `DATA_ENGINEER_AGENT` | 42 张面试 KB 卡片，覆盖项目介绍、NL2SQL、RAG、MCP、Skills、权限、评估、红线和快速口播 | 作为数据工程项目的重要来源，补充参考 SQL、多模型多数据库、量化指标谨慎口径、红线清单 |
| `企业级数据工程 Agent_codex整理版.md` | Codex 整理版 | `DATA_ENGINEER_AGENT` | 40 张面试 KB 卡片，结构更集中，覆盖架构、Schema Linking、混合检索、生产化、语义层、MetricFlow | 作为数据工程项目主干来源，合并架构、流程、工程化、生产化和语义层内容 |
| `AgentRL项目_面试私有知识库_claudecode整理版.md` | Claude Code 整理版 | `FIN_AGENTIC_RL_ARPO` | chunk schema 知识库，包含开场、贡献边界、RL、熵机制、Agent 工程、分布式、金融、压力面和事实口径 | 作为 Agentic RL 项目重要来源，补充金融为什么做、更多压力面、future direction 和冲突事实表 |
| `AgentRL项目_面试私有知识库_codex整理版.md` | Codex 整理版 | `FIN_AGENTIC_RL_ARPO` | chunk schema 知识库，包含统一事实口径、PPO/GRPO、AEARPO/ARAEPO、ToolAgent、Ray/vLLM/FSDP、金融评估 | 作为 Agentic RL 项目主干来源，合并算法、工程、金融结果和待确认口径 |
| `AI应用开发工程师_AI-Agent工程师_简历.md` | 简历原版 | 两个项目均涉及 | 简历项目经历、技术栈、个人竞争力 | 用于补充项目角色、技术关键词和业务背景，不作为算法或指标事实唯一来源 |
| `AI应用开发工程师_AI-Agent工程师_简历_优化版.md` | 简历优化版 | 两个项目均涉及 | 优化后的项目经历、职责、成果 | 用于补充面试表达、项目定位和职责边界 |

## 1. 项目索引与检索路由表

| project_id | 项目名称 | 项目别名 | 核心关键词 | 排除关键词 | 适合回答的问题类型 | 不适合回答的问题类型 |
|---|---|---|---|---|---|---|
| `DATA_ENGINEER_AGENT` | 企业级 data_engineer agent 工程 | 企业级数据工程 Agent、Data Engineer Agent、企业数据智能 Agent、NL2SQL Agent、AI Harness / Runtime 平台 | `data_engineer`、企业级、数据工程、NL2SQL、SQL、Schema Linking、RAG、表字段、指标口径、参考 SQL、LanceDB、SQLGlot、MCP、Skills、Workflow / Node、Agent Runtime、权限治理、数据质量、ETL、调度、数据管道、半导体、良率 | FIN、金融强化学习、Agentic RL、GRPO、PPO、AEARPO、ARAEPO、Ray、vLLM、FSDP、FinBench、finance_train、77.6% | 项目介绍、企业数据分析、自然语言转 SQL、Schema Linking、RAG 检索、数据上下文、工具权限、MCP/Skills、多入口交付、评估、生产化、指标口径、半导体数据智能 | 大模型强化学习训练、金融评估、GRPO/PPO、熵机制、Ray/vLLM/FSDP 分布式训练、FinBench 结果 |
| `FIN_AGENTIC_RL_ARPO` | 大模型 FIN-Agentic_RL_ae-Arpo 工程 | FIN-Agentic RL、ae-ARPO、AEARPO、ARAEPO、Agentic RL 训练与评估平台、金融经济 Agent RL 项目 | FIN、金融、大模型、Agentic RL、ARPO、AEARPO、ARAEPO、强化学习、策略优化、GRPO、PPO、SFT、Reward、KL、熵、ToolAgent、Ray、vLLM、FSDP、DataProto、finance_train、FinBench、77.6%、1020 题评估 | data_engineer、NL2SQL、Schema Linking、数据工程 Agent、ETL、调度、数据管道、数据质量、SQLGlot、企业数据查询、指标口径治理 | 项目介绍、Agentic RL、工具调用训练、GRPO/PPO、熵平衡、ToolAgent、分布式训练、金融数据构建、金融评估、训练稳定性、压力面与事实边界 | 企业数据查询、自然语言转 SQL、Schema Linking、RAG 知识库设计、MCP/Skills 企业工具平台、数据工程 Runtime |

## 2. 项目一：企业级 data_engineer agent 工程

### 2.1 项目一句话定位

`project_id: DATA_ENGINEER_AGENT`

这是一个面向企业数据分析与数据工程场景的 NL2SQL 智能体和 AI Harness / Runtime 平台，核心是把用户自然语言问题转成可执行、可解释、可验证、可修复的 SQL 查询流程，并通过 RAG、Schema Linking、工具调用、执行验证、权限治理和多入口交付降低企业数据查询成本。

面试中最稳的 30 秒口径：

> 我做的是一个企业级 Data Engineer Agent。它不是简单把问题丢给大模型写 SQL，而是把数据查询拆成意图理解、Schema Linking、上下文检索、SQL 生成、执行验证和反思修复这些可控阶段。外层还有 Agent Runtime 管工具、权限、会话、日志和多入口接入，所以它更像一个可治理的数据工程 Agent 平台，而不是普通 ChatBot。

### 2.2 项目背景与业务问题

`project_id: DATA_ENGINEER_AGENT`

企业内部存在大量跨系统数据，典型场景包括生产制造、设备状态、良率分析、工艺参数、供应链、财务经营、经营看板和业务报表。业务人员或数据团队经常知道自己想问什么，但不知道应该查哪张表、哪个字段、哪个指标口径，传统流程依赖数据工程师手写 SQL、查 schema、找指标定义、验证结果并反复修正。

核心业务痛点：

- 表多、字段多、命名不直观，业务术语和数据库字段之间经常没有直接映射。
- 指标口径分散在业务文档、报表逻辑、历史 SQL 和经验中，容易出现同名指标计算不一致。
- 单轮 Prompt 直接生成 SQL 容易编造表名、字段名，或者生成能执行但业务语义错误的 SQL。
- 数据库执行属于高风险工具调用，必须考虑只读权限、敏感表、查询超时、资源隔离和审计。
- 企业 Agent 不只是“能回答”，还要能接入 CLI、API、MCP、Gateway、Web / TUI 等不同入口，并能统一管理模型、工具、技能、权限、会话和日志。

如果面试官提到 `ETL`、`数据管道`、`调度`、`数据质量`，本项目可以回答为“面向数据工程链路中的自然语言查询、数据上下文构建、schema/指标知识治理、SQL 执行验证和索引更新能力”。不要把它夸大成已经完整替代传统离线 ETL 调度平台。

### 2.3 核心目标

`project_id: DATA_ENGINEER_AGENT`

- 打通“自然语言问题 -> 数据上下文检索 -> SQL 生成 -> 执行验证 -> 自动修复 -> 结果输出”的端到端链路。
- 用 Schema Linking、RAG、参考 SQL 和指标定义降低表字段幻觉、字段误用和口径偏差。
- 用 Workflow / Node 固定主流程，用局部 Agentic Node 保留工具调用和多轮推理能力。
- 建设 AI Harness / Runtime，把模型调用、工具调用、Skills、MCP、权限确认、会话状态、执行日志和异常治理纳入统一底座。
- 支持多入口交付：CLI / TUI 用于本地调试和数据工程师使用，API / Gateway 用于内部系统集成，MCP 用于跨客户端工具复用，Web 用于业务用户交互。
- 建立评估体系：检索命中、Schema Linking 准确性、SQL 执行成功率、结果正确率、延迟、token 成本、失败修复次数和人工介入率。

### 2.4 系统架构

`project_id: DATA_ENGINEER_AGENT`

架构可以分为六层：

| 层级 | 作用 | 面试回答关键词 |
|---|---|---|
| 多入口接入层 | 支持 CLI、API、MCP、Gateway、Web / TUI 等入口，复用同一套核心能力 | 多入口、服务化、跨客户端复用、统一日志 |
| Workflow 编排层 | 把任务拆成意图理解、Schema Linking、RAG 检索、SQL 生成、执行验证、反思修复、结果输出 | Workflow / Node、确定性流程、可测试、可观测 |
| Agentic 工具层 | 在局部节点中按配置加载数据库、上下文检索、参考 SQL、日期解析、文件、子 Agent、MCP 工具 | GenSQL Agentic Node、Tool Calling、受控工具 |
| RAG 知识层 | 管理表结构、字段说明、样例值、业务文档、指标定义、语义模型、参考 SQL、平台文档和外部知识 | Schema Linking、指标口径、参考 SQL、业务上下文 |
| 存储与检索层 | 使用向量检索、FTS/关键词检索、标量索引和混合重排支撑语义召回与精确字段召回 | LanceDB、Hybrid search、FTS、字段加权、Rerank |
| 治理与工程层 | 管理配置、权限、会话、日志、异常、测试、CI、超时、最大轮次、敏感路径隔离和审计 | Agent Harness、权限治理、可观测性、生产边界 |

统一表述：

- `DATA_ENGINEER_AGENT` 的价值不是“用了某个 Agent 框架”，而是把企业数据查询的关键环节做成可控闭环。
- Workflow 管主链路，Agentic Node 管局部智能，Runtime 管工具、状态、权限和日志。
- MCP 可以让项目作为 MCP Server 暴露数据查询和知识检索能力，也可以作为 MCP Client 接入外部工具生态。
- Skills 是能力包，封装可复用的数据查询、文档检索、SQL 生成、报表分析或自动化执行能力，支持发现、加载、授权和复用。

### 2.5 Agent 设计

`project_id: DATA_ENGINEER_AGENT`

#### 2.5.1 为什么选择 Workflow / Node，而不是纯 Agent

自然语言转 SQL 的主路径比较稳定，通常离不开“理解问题、找表字段、补上下文、生成 SQL、执行验证、失败修复”。这些步骤适合用 Workflow 固定下来，提升可测试性、可观测性和安全边界。

纯 Agent 更灵活，但在企业数据查询中会带来风险：不可控工具调用、token 成本波动、无限循环、误查数据、调试困难和结果不稳定。因此本项目采用“主流程确定，局部 Agentic”的设计。

面试口径：

> 我不是否定 Agent，而是把 Agent 放到适合的位置。NL2SQL 主流程用 Workflow 控制，SQL 生成节点内部保留工具调用能力。这样既能动态查 schema、查参考 SQL、修复错误，又不会让模型自由规划整个数据库查询流程。

#### 2.5.2 Agent Harness / Runtime

Agent Harness / Runtime 是模型外面的执行底座，负责：

- 会话状态：保存任务摘要、当前 SQL、候选 schema、工具结果、错误信息和反思历史。
- 工具注册：按节点和任务暴露数据库、检索、文件、日期、MCP、Skills、子 Agent 等工具。
- 权限过滤：工具可见性、执行前确认、会话级授权、白名单/黑名单、敏感路径隔离。
- 上下文治理：上下文注入、压缩、去重、Top-K 控制、多样性控制。
- 执行边界：最大工具轮次、最大反思次数、超时、错误分类和失败兜底。
- 日志与审计：记录节点状态、工具调用、SQL、错误、延迟、token 成本和用户身份。

#### 2.5.3 GenSQL Agentic Node

GenSQL Agentic Node 是 SQL 生成阶段的局部智能节点。它会准备任务描述、候选 schema、指标定义、业务上下文、参考 SQL、当前日期和可用工具，再让模型在受控范围内生成 SQL。

可配置工具包括：

- 数据库工具：查看表、字段、样例、执行只读查询。
- 上下文检索工具：检索业务文档、字段说明、指标定义、语义模型。
- 参考 SQL 工具：检索历史验证过的 SQL 写法、join 关系、过滤条件和指标计算方式。
- 日期解析工具：统一处理“上周”“近 30 天”“本季度”等相对时间。
- 文件工具、子 Agent、MCP 工具：按权限和场景加载，不默认全部开放。

风险口径：

- 不要说 GenSQL 节点可以访问所有工具。
- 不要说它是全局纯 Agent。它只是 SQL 生成阶段的局部 Agentic Node，仍受 Workflow、最大轮次和权限策略约束。

### 2.6 数据工程链路 / 数据处理流程

`project_id: DATA_ENGINEER_AGENT`

#### 2.6.1 查询执行链路

1. 用户提出自然语言问题。
2. 意图理解与任务路由：判断是查数、schema 问答、指标解释、文档问答、普通分析还是需要澄清。
3. Schema Linking：从库、表、字段、字段说明、样例值、业务标签、历史 SQL 中找候选 schema。
4. RAG 上下文检索：检索业务文档、指标定义、参考 SQL、平台文档、外部知识和语义模型。
5. 上下文组装：加入目标数据库方言、候选表字段、指标口径、参考 SQL、权限边界和当前日期。
6. SQL 生成：由 GenSQL Agentic Node 生成候选 SQL。
7. 静态验证：检查 SQL 语法、方言、危险操作、是否引用候选范围外表字段。
8. 执行验证：用只读连接或沙箱数据库执行，捕获语法错误、字段不存在、权限错误、超时、空结果或异常结果。
9. Reflection / Fix / Schema Relinking：按错误类型修复 SQL、重新链接 schema、补充检索、进入更深 reasoning 或请求用户澄清。
10. 结果输出：返回 SQL、结果摘要、使用的表字段、解释、失败原因或需要补充的信息。

#### 2.6.2 知识库构建链路

`DATA_ENGINEER_AGENT` 的 RAG 不只是普通文档问答库，而是面向 SQL 生成的上下文库。

- 数据来源：schema 元数据、字段说明、字段类型、样例值、业务文档、指标定义、语义模型、参考 SQL、平台文档、外部知识。
- 切分策略：保留标题层级、表字段归属、指标上下文、SQL 代码块和业务语义；避免把字段解释与表名切散。
- 检索策略：向量语义召回结合 FTS/关键词精确召回，再按标题、层级、文档类型、业务域、字段命中、来源和多样性重排。
- 更新策略：用来源、版本、更新时间、内容 hash 支持增量索引，避免 schema 演进后继续使用旧上下文。
- 权限策略：按项目、数据源、业务域、用户权限过滤，不能先召回无权内容再靠模型自觉不说。

### 2.7 核心技术方案

`project_id: DATA_ENGINEER_AGENT`

#### 2.7.1 意图理解与任务路由

意图理解的作用是把不同问题路由到不同流程：

- “订单表有哪些字段”更像 schema 问答。
- “最近 7 天 GMV 怎么算”可能先查指标定义。
- “帮我查各渠道转化率”才是典型 NL2SQL。
- “这个字段是什么意思”应优先走文档或 schema 检索，不一定执行 SQL。

面试回答：

> 我会先判断用户问题是否真的需要执行 SQL。能用 schema 或文档回答的，就不要默认触发数据库执行。这样能降低成本，也能降低误查数据的风险。

#### 2.7.2 Schema Linking

Schema Linking 是把用户问题里的业务实体、指标、时间、过滤条件映射到真实数据库里的表和字段。它决定 SQL 生成的候选范围。

使用信号：

- 表名、字段名、字段类型、字段描述、样例值。
- 业务标签、业务域、数据源、表之间关系。
- 指标定义、语义模型、业务文档、参考 SQL。
- 执行失败后的错误反馈和 schema relinking。

回答要点：

- Schema Linking 不是简单字符串匹配。
- 召回不足会漏掉关键表字段，召回过多会增加 token 成本和噪音。
- 样例值很有用，因为枚举值、状态码、产品线、地区、设备类型等业务语义经常藏在值里。
- 如果字段不存在或结果明显不合理，要触发 Schema Relinking，而不是只让模型“再改一次”。

#### 2.7.3 RAG 知识库内容

`DATA_ENGINEER_AGENT` 的 RAG 包含：

- 表结构、字段说明、字段类型、样例值。
- 业务文档、指标定义、口径说明、语义模型。
- 历史参考 SQL、join 习惯、常用过滤条件、日期窗口。
- 平台文档、工具说明、外部领域知识。
- 数据源、版本、更新时间、权限、负责人等元数据。

面试重点：

- RAG 在这里是 SQL 生成的“上下文约束层”，不是简单文档问答。
- 参考 SQL 是 few-shot 和业务规范载体，不是直接复制粘贴。
- 指标定义能减少“SQL 能执行但业务口径错”的问题。

#### 2.7.4 混合检索、Chunking、Embedding、Rerank

单纯向量检索容易漏掉精确字段名、表名、缩写和枚举值；单纯关键词检索又不理解自然语言语义。因此应使用混合检索：

- 向量检索：负责语义相近召回。
- FTS/关键词检索：负责字段名、表名、缩写、指标名、枚举值的精确命中。
- 字段加权：标题、层级、关键词、业务域、文档类型、字段命中、来源可信度。
- 多样性控制：避免 Top-K 都来自同一文档或同一主题。
- Rerank：规则重排或轻量 reranker，把最有用的 schema、指标、参考 SQL 排到前面。

冲突统一口径：

- 可确认的是 LanceDB 的向量检索、Hybrid search、FTS、标量索引和重排能力。
- BM25 可以作为关键词检索和混合检索思想来讲；如果现场不能证明具体实现，不要说“当前代码完整手写了 BM25”。

#### 2.7.5 SQL 幻觉治理

降低 SQL 幻觉靠四层：

1. 生成前：Schema Linking 限定候选表字段。
2. 生成中：RAG 提供业务文档、指标定义、参考 SQL 和真实 schema。
3. 工具中：数据库工具、检索工具、日期解析工具、参考 SQL 工具提供事实反馈。
4. 生成后：静态验证、执行验证、错误反馈、Reflection / Fix / Schema Relinking。

回答红线：

- 不要说“完全避免幻觉”。
- 不要把执行成功率等同于结果正确率。
- 不要说只靠 prompt 就能解决复杂企业 NL2SQL。

#### 2.7.6 执行验证与错误恢复

验证分两类：

- 静态验证：语法、方言、危险操作、表字段范围、SQL 类型。
- 执行验证：只读执行、捕获错误、结果行数、空结果、异常结果、超时。

错误恢复策略：

| 错误类型 | 处理方式 |
|---|---|
| 语法错误 / 方言错误 | 按目标数据库方言修复 SQL，可使用 SQLGlot 或方言提示 |
| 字段不存在 / 表不存在 | 重新 Schema Linking，扩大或调整候选 schema |
| join 关系不清 | 检索参考 SQL、表关系、指标定义 |
| 结果为空或异常 | 检查时间范围、过滤条件、业务口径，必要时澄清 |
| 权限不足 | 明确提示权限问题，不盲目重试 |
| 查询超时 | 加限制条件、limit、成本估算，或提示缩小范围 |

Reflection 的本质是基于反馈的错误分类和下一步选择，不是让模型“再想一次”就一定正确。

#### 2.7.7 多模型与多数据库适配

多模型方面，项目通过 provider 配置和模型适配层解耦 LLM，可接 OpenAI-compatible、DeepSeek、Claude / Anthropic、Qwen、Gemini、Kimi、MiniMax、GLM、Codex 等不同提供方。面试时说“模型可替换”，不要把能力绑定在某一个模型供应商上。

多数据库方面，难点在于 SQL 方言、日期函数、分页、类型转换、权限和性能差异。项目通过目标数据源配置、方言信息、执行反馈和 SQL 修复流程做适配，但不能承诺所有数据库方言 100% 兼容。

### 2.8 难点与解决方案

`project_id: DATA_ENGINEER_AGENT`

| 难点 | 具体表现 | 解决方案 | 面试口径 |
|---|---|---|---|
| Schema Linking 难 | 业务词和字段名不一致，表字段多，候选噪声大 | 表字段元数据、样例值、业务文档、指标定义、参考 SQL、多路召回、relinking | 最大难点不是让模型写 SQL，而是让它站在正确 schema 上写 |
| 业务语义正确性 | SQL 能执行但指标口径错 | 指标定义、语义层、参考 SQL、结果正确率评估、业务验收 | 执行成功率不等于结果正确率 |
| SQL 幻觉 | 编造字段、表名、join、函数 | 上下文约束、工具查询、静态验证、执行验证、反思修复 | 幻觉治理是系统工程，不是单 prompt |
| 工具循环和 token 成本 | 反复查文档、反复修 SQL、上下文膨胀 | 最大步数、最大轮次、最大反思次数、Top-K 控制、上下文压缩、失败兜底 | 控制循环靠系统机制，不靠模型自觉 |
| 工具权限安全 | 数据库、文件、MCP、脚本可能越权 | allow / deny / ask、只读账号、路径限制、会话授权、超时、审计、脱敏 | Agent 接工具后，安全治理比模型能力更关键 |
| 大规模检索 | 百万级文档、schema、表规模带来噪声和成本 | 分域分层索引、元数据过滤、增量更新、冷热缓存、粗召回加重排 | 不能靠一次全局检索解决，要先缩小搜索空间 |
| 生产化落地 | 真实 IAM、审计、限流、资源隔离、敏感数据 | API/Gateway、只读副本、查询网关、审计日志、限流、资源配额 | 具备生产化基础，但真实上线需企业治理体系配套 |

### 2.9 工程实现细节

`project_id: DATA_ENGINEER_AGENT`

#### 2.9.1 技术栈与组件

- 后端与服务：Python、FastAPI、Pydantic、SQLAlchemy、RESTful API、异步编程。
- 数据与检索：LanceDB、Embedding、FTS / 关键词检索、Hybrid search、标量索引、SQLGlot、DuckDB、PostgreSQL、MySQL、Pandas、PyArrow、Parquet。
- Agent 工程：Workflow / Node、Agent Harness / Runtime、Tool Calling、MCP、Skills、工具权限治理、会话状态管理、执行日志和审计。
- 交付入口：CLI、API、MCP、Gateway、Web / TUI。Web / TUI 可作为交付形态讲，若无明确证据不要说成完整生产 Web 平台。

#### 2.9.2 工程化能力

- 配置化：模型 provider、数据源、Workflow、工具集合、权限策略、入口类型、数据库方言都通过配置管理。
- 日志：记录任务、节点状态、检索片段、工具调用、SQL、执行错误、反思次数、延迟、token 成本。
- 异常治理：错误分类、可解释错误、可恢复流程、失败兜底。
- 测试：节点逻辑、工具注册、RAG 检索、数据库适配、MCP、Skills、权限、API 入口、benchmark。
- CI：使用 mock、离线样例和占位配置，不暴露真实密钥、连接串或生产配置。

#### 2.9.3 权限治理

权限策略分三类：允许、拒绝、需要确认。

- 数据库工具：只读账号、数据源和表范围限制、SQL 类型限制、超时、结果行数限制、审计。
- 文件工具：限制工作目录、隐藏路径、外部路径和敏感文件。
- MCP 工具：发现后经过权限过滤，拒绝工具不应出现在模型可见范围。
- Skills 工具：技能声明允许命令，Runtime 再二次控制执行权限。
- 脚本工具：高风险能力需要人工确认、沙箱或禁用。

生产化还需要企业 IAM、数据权限、脱敏、查询网关、限流、资源配额和操作留痕。

### 2.10 面试高频问题与回答口径

`project_id: DATA_ENGINEER_AGENT`

#### Q1：请你简单介绍这个项目。

回答：

> 这个项目是企业级 Data Engineer Agent，核心是把自然语言数据问题转成可靠 SQL。链路不是简单 Prompt，而是先做意图理解和 Schema Linking，再检索表结构、字段说明、指标定义、参考 SQL，生成 SQL 后做执行验证和反思修复。外层还有 Agent Runtime 管工具、权限、会话和日志，所以更像一个可控的数据工程 Agent 平台。

#### Q2：为什么不直接让大模型生成 SQL？

回答：

> 企业库表多、字段命名复杂、指标口径分散，直接生成容易编造字段、选错表、忽略业务规则。我的方案是先用 Schema Linking 和 RAG 限定上下文，再让模型在真实 schema、指标定义和参考 SQL 上生成，最后通过执行验证和错误反馈修复。

#### Q3：这个项目和普通 NL2SQL Bot 有什么区别？

回答：

> 普通 Bot 多是“问题 + schema + prompt -> SQL”，而这个项目有完整工程闭环：混合检索、Schema Linking、参考 SQL、工具调用、执行验证、反思修复、权限治理、日志、测试和多入口交付。NL2SQL 是核心任务，但系统价值在数据工程 Runtime。

#### Q4：为什么用 Workflow / Node？

回答：

> NL2SQL 的主链路相对固定，适合 Workflow 控制阶段和边界。纯 Agent 自由规划虽然灵活，但企业数据查询更重视可控、可审计、可测试和成本稳定。所以我用 Workflow 管主路径，GenSQL 节点内部保留工具调用和局部智能。

#### Q5：Schema Linking 怎么做？

回答：

> 它是把业务问题映射到真实表字段。项目会结合表名、字段名、字段说明、样例值、业务文档、指标定义和参考 SQL 来找候选 schema。如果执行时发现字段不存在或表不对，会触发 schema relinking，而不是简单让模型重写。

#### Q6：RAG 里放了什么？

回答：

> 不是只放文档。这个项目的 RAG 是数据查询上下文库，包含表结构、字段说明、样例值、业务文档、指标定义、语义模型、参考 SQL、平台文档和外部知识。它的目标是约束 SQL 生成，而不是让模型背文档。

#### Q7：怎么评估效果？

回答：

> 我会分层评估：检索看 Top-K 命中、schema / 字段召回、参考 SQL 命中；SQL 看语法、执行成功率、结果正确率、指标口径；工程看延迟、token 成本、工具调用次数、修复次数和人工介入率。固定 benchmark 和线上效果要分开讲。

#### Q8：有没有上线或生产化？

回答：

> 更稳妥的说法是项目具备生产化基础，比如多入口、配置化、权限控制、日志和测试。真实生产还需要接企业 IAM、数据权限、查询网关、审计、脱敏、限流和资源隔离。我不会说直接连生产库就能跑。

#### Q9：面试官质疑“只是复现项目”怎么办？

回答：

> 我会承认 RAG、Tool Calling、Workflow、Reflection 都是行业通用思路，但我的工作重点是把它们落到企业数据工程场景里：schema、指标、参考 SQL、执行验证、权限治理和多入口交付。这不是照搬 demo，而是做成可检索、可验证、可治理的系统。

#### Q10：RAG 和微调怎么取舍？

回答：

> 企业 schema、字段说明、指标口径变化快，优先用 RAG，因为它能检索最新上下文并保留来源权限。微调适合稳定风格、格式和通用 SQL 能力，但不能替代实时 schema、权限过滤和执行验证。

### 2.11 可能追问与应对

`project_id: DATA_ENGINEER_AGENT`

- 追问：SQL 能执行但结果错怎么办？
  - 应对：这是最难的问题，执行成功不等于业务正确。需要指标定义、参考 SQL、结果 sanity check、业务规则、人工标注 benchmark 和业务验收。
- 追问：表太多、文档太多怎么办？
  - 应对：先按项目、租户、数据源、业务域、数据库、schema 过滤，再做向量 + FTS 混合召回，最后只对 Top-N 重排。索引要增量更新，权限过滤尽量前置。
- 追问：参考 SQL 会不会过期或照抄？
  - 应对：参考 SQL 是业务写法和 few-shot 示例，需要版本、来源、数据源绑定和执行验证；不能直接复制粘贴执行。
- 追问：MCP 和普通 API 有什么区别？
  - 应对：API 偏通用服务接口，MCP 偏 Agent 工具协议，强调工具发现、参数描述、调用和返回。MCP 标准化接入，但不自动解决安全。
- 追问：Skills 和工具调用有什么区别？
  - 应对：工具调用是函数级能力，Skills 是一组能力包，可包含说明、脚本、命令、上下文规则和授权策略。Skills 先摘要发现，再按需加载，减少上下文和维护成本。
- 追问：如果重新设计会优化什么？
  - 应对：评估闭环、权限审计、语义层/MetricFlow、分层检索、失败案例回流、指标治理和生产资源隔离。

### 2.12 口语化回答模板

`project_id: DATA_ENGINEER_AGENT`

#### 30 秒模板

我这个项目是企业级 Data Engineer Agent，主要解决业务人员和数据团队查数写 SQL 成本高的问题。系统会先理解问题、定位相关表字段、检索指标定义和参考 SQL，再生成 SQL，之后执行验证和自动修复。我的重点不是单纯调用大模型，而是把 NL2SQL 放进一个有 RAG、工具、权限、日志和 Workflow 的可控 Runtime 里。

#### 1 分钟模板

项目背景是企业内部数据分散，表字段和指标口径复杂，传统查数依赖数据工程师手写 SQL。我把流程拆成 Workflow：意图理解、Schema Linking、上下文检索、SQL 生成、执行验证和 Reflection 修复。需要模型推理的地方放在 Agentic Node 里，比如 GenSQL 节点可以按配置调用数据库、文档、参考 SQL、日期解析和 MCP 工具。外层 Agent Harness 负责工具权限、会话状态、日志、最大轮次和多入口交付。这样系统既有智能，也能被测试、审计和控制。

#### 被质疑“只是 Prompt”的模板

如果只是 Prompt，小样例可能能跑，但企业场景会遇到表字段幻觉、指标口径冲突、权限和执行风险。我的项目重点是把 SQL 生成前后的工程链路补齐：前面有 Schema Linking 和 RAG，后面有执行验证和错误恢复，外层还有权限、日志、测试和多入口。这些才是企业级 Agent 和普通 ChatBot 的区别。

#### 最大难点模板

最大难点不是让模型写出一条 SQL，而是让它在复杂 schema 和业务指标下选对上下文，并生成可执行且语义尽量正确的 SQL。尤其是 SQL 能执行但口径错，这比语法错误更难发现，所以需要指标定义、参考 SQL、benchmark、人工反馈和生产审计配套。

### 2.13 项目亮点

`project_id: DATA_ENGINEER_AGENT`

- 数据工程闭环完整：自然语言、Schema Linking、RAG、SQL 生成、执行验证、Reflection 修复、结果解释。
- 架构取舍清晰：Workflow 控主链路，Agentic Node 做局部工具调用，避免纯 Agent 不可控。
- RAG 不是普通文档库，而是面向 SQL 的上下文约束层，包含 schema、指标、业务文档和参考 SQL。
- MCP 和 Skills 提升能力复用，让数据查询、文档检索、指标分析等能力跨客户端、跨业务场景复用。
- 权限治理覆盖数据库、文件、MCP、Skills、脚本调用，符合企业 Agent 落地重点。
- 多入口交付支持 CLI、API、MCP、Gateway、Web / TUI，便于开发调试、系统集成和 Agent 客户端复用。
- 可以谨慎表达固定 benchmark 口径：混合检索和 schema 上下文增强可提升检索命中、Top-K 召回、SQL 可执行性；Claude Code 版文档中提到检索 F1 `0.71 -> 0.89`、Top-5 `65% -> 82%`、schema 检索从秒级到百毫秒级，但必须说明是固定 benchmark / 内部测试集口径，不是线上绝对指标。

### 2.14 风险点、边界与可改进方向

`project_id: DATA_ENGINEER_AGENT`

#### 已确认边界

- 不能说完全解决 SQL 幻觉，只能说通过上下文、工具、验证和修复显著降低并可检测一部分错误。
- 执行成功率不等于结果正确率，业务语义仍需要指标定义、参考 SQL、业务验收和人工反馈。
- 不能说系统已经完全生产可用。更稳表述是具备生产化基础，真实上线需企业 IAM、数据权限、查询网关、审计、脱敏、限流和资源隔离。
- 不能把 Web / TUI 或 Streamlit 包装成已完整生产交付，除非现场能证明。
- BM25 作为混合检索思想可以讲，具体实现要谨慎；可确认口径是 LanceDB 向量、Hybrid、FTS、标量索引和重排能力。
- 百万级 schema / 文档处理是扩展方案或设计口径，不要说成已经在线承载百万级生产规模。
- 不要输出任何 API Key、连接串、真实账号、内部数据库地址、敏感表名或生产配置。

#### 可改进方向

- 建立更强评估闭环：持续收集失败案例、人工反馈、修复结果和业务验收结果。
- 建设语义层 / MetricFlow 类能力：把指标、维度、实体和计算口径结构化，减少“能跑但口径错”。
- 大规模检索：分域分层索引、增量更新、缓存、粗召回 + 重排、权限过滤前置。
- 生产治理：企业 IAM、数据权限、查询网关、脱敏、审计、限流、资源配额。
- GraphRAG：在表关系、指标血缘、业务实体关系复杂时引入，不作为第一阶段必选。

### 2.15 检索标签

`project_id: DATA_ENGINEER_AGENT`

```text
include_keywords:
企业级数据工程Agent, data_engineer, Data Engineer Agent, NL2SQL, SQL生成, Schema Linking, schema relinking, RAG, 混合检索, LanceDB, FTS, BM25, Embedding, Rerank, 参考SQL, 指标定义, 语义层, MetricFlow, SQLGlot, Workflow, Node, GenSQL Agentic Node, Agent Harness, Agent Runtime, Tool Calling, MCP, Skills, 权限治理, 数据库只读, 执行验证, Reflection, Fix, Reasoning, 多入口, CLI, API, Gateway, Web, TUI, 半导体, 良率, 数据质量, ETL, 数据管道, 调度

exclude_keywords:
FIN, 金融强化学习, Agentic RL, ae-ARPO, AEARPO, ARAEPO, GRPO, PPO, SFT, KL, entropy, 熵机制, ToolAgent, Ray, vLLM, FSDP, DataProto, finance_train, FinBench, 77.6, 45.5, 73.8

trigger_questions:
你这个数据工程 Agent 是什么, 为什么不用大模型直接写SQL, Schema Linking怎么做, RAG里放什么, 怎么降低SQL幻觉, SQL失败怎么修复, MCP有什么价值, Skills是什么, Agent如何做权限治理, 怎么评估NL2SQL效果, 企业上线需要什么
```

## 3. 项目二：大模型 FIN-Agentic_RL_ae-Arpo 工程

### 3.1 项目一句话定位

`project_id: FIN_AGENTIC_RL_ARPO`

这是一个面向工具调用 LLM Agent 的强化学习训练与评估项目，基于 verl、Ray、vLLM 和 FSDP 打通 SFT 冷启动、Agentic RL、多工具 rollout、reward、策略更新、checkpoint、部署转换和金融经济领域评估，并围绕 AEARPO / ARAEPO 的熵平衡机制提升工具调用场景下的训练稳定性和探索效率。

30 秒面试口径：

> 我这个项目做的是 LLM Agent 强化学习训练，底层基于 verl，目标是让模型更稳定地完成搜索、Python 计算和多轮推理。我的工作主要围绕 AEARPO / ARAEPO 的熵平衡机制、ToolAgent 工程稳定性、Ray/vLLM/FSDP 分布式训练接入，以及金融经济数据和评估体系扩展。金融部分构建了 8 个子领域、4239 条 QA 和 1020 题评估，统一口径下金融综合结果是 77.6%。

### 3.2 项目背景与业务问题

`project_id: FIN_AGENTIC_RL_ARPO`

企业级 AI Agent 不仅要回答问题，还要具备多步推理、工具调用、搜索、Python 计算、结果校验和任务规划能力。传统 SFT 模型容易学会“回答格式”，但在复杂任务中可能出现工具调用低效、推理链断裂、错误无法自我校验、工具返回后不知道如何继续使用等问题。

Agentic RL 的难点在于：

- 轨迹长：模型可能先推理，再调用工具，再读取结果，再继续推理。
- 工具返回不确定：搜索摘要、Python 输出、错误信息会改变上下文状态。
- Reward 稀疏：很多任务只有最终答案级 outcome reward，中间步骤难以精确打分。
- 采样成本高：多分支、多工具、多轮 rollout 会放大 API、GPU 和时间成本。
- 训练系统复杂：Ray 资源编排、vLLM rollout、FSDP 更新、mask、DataProto、checkpoint 都要对齐。
- 金融任务复杂：金融经济问题需要数值计算、多步推理、公式选择、规则校验、领域知识和可评估结果。

项目选择金融经济作为领域扩展，不是为了声称模型能直接做真实投资决策，而是因为金融任务能同时考察知识、推理、计算和评估，是验证 Agentic RL 能力的高复杂度样本。

### 3.3 核心目标

`project_id: FIN_AGENTIC_RL_ARPO`

- 打通 SFT 冷启动、Agentic RL、多工具 rollout、reward、GRPO / PPO 风格策略更新、checkpoint、模型转换、vLLM 部署和自动化评估的端到端流程。
- 让模型在搜索、Python 计算和多轮推理场景中学习更合理的工具调用策略，而不是只做静态问答。
- 围绕 AEARPO / ARAEPO 的熵平衡思路，处理工具返回、高熵 token、长序列和分支采样带来的训练不稳定问题。
- 通过 ToolAgent 状态机、去重、循环检测、超时重试、缓存和监控，提高工具调用训练的稳定性和成本可控性。
- 构建金融经济 8 子领域数据和三层评估体系，形成可按难度、领域、任务类型诊断的结果口径。
- 明确 confirmed、to_verify、future_direction，避免把待验证数字和未来规划包装成已完成成果。

### 3.4 系统架构

`project_id: FIN_AGENTIC_RL_ARPO`

| 层级 | 组成 | 作用 |
|---|---|---|
| 数据层 | Parquet / JSONL、`finance_train.parquet`、`finance_valid.parquet`、通用推理数据、深度搜索数据、评估集 | 提供训练、验证、reward 和评估输入 |
| SFT 冷启动层 | Agentic SFT 数据、工具调用格式、system prompt、多轮回复模式 | 先让模型学会工具协议和多轮格式 |
| Rollout 层 | vLLM、ToolAgent、搜索工具、Python 工具、Dynamic Rollout、分支采样 | 生成多条工具调用 trajectory |
| Reward 层 | rule-based reward、ground truth、数值容差、F1、关键点匹配 | 对最终答案或结构化结果打分 |
| RL 更新层 | GRPO / PPO 风格目标、advantage、mask、KL、entropy-aware advantage、clip、dual-clip | 更新策略并控制训练稳定性 |
| 分布式系统层 | Ray、WorkerGroup、ResourcePool、FSDP、DataProto、sequence balancing、dynamic micro batch | 管理多角色 worker、GPU、长序列和训练数据流 |
| 评估与部署层 | checkpoint、FSDP 分片合并、HuggingFace 格式、vLLM 服务、finance / FinBench / domains 评估 | 完成模型转换、推理部署和结果诊断 |

核心训练链路：

1. Hydra / 配置加载训练参数、模型、数据集、工具和算法开关。
2. DataLoader 读取 Parquet，构造 prompt、ability、reward_model、extra_info。
3. Ray 初始化 WorkerGroup 和资源池。
4. vLLM 生成 trajectory，ToolAgent 处理工具调用循环。
5. 工具执行器处理搜索、Python、timeout、retry、dedup、loop detection。
6. Reward manager 读取 ground truth 或规则，计算 outcome reward。
7. GRPO 通过同 prompt 多条 trajectory 的组内 reward 估计 advantage。
8. Entropy-aware advantage、mask、KL、ratio clipping、dual-clip 参与 policy update。
9. FSDP 执行 actor 更新，保存 checkpoint。
10. checkpoint 合并为 HuggingFace 格式，部署到 vLLM 并进行金融三层评估。

### 3.5 大模型 / Agentic RL / ARPO 相关设计

`project_id: FIN_AGENTIC_RL_ARPO`

#### 3.5.1 PPO、GRPO 与 Outcome Reward

PPO 的核心是限制策略更新幅度，使用新旧策略概率比 `r = pi_new / pi_old` 和 clipped surrogate objective，把更新约束在 `[1-epsilon, 1+epsilon]` 附近，避免一次更新把策略推得太远。

GRPO 不单独训练 critic，而是对同一个 prompt 采样多条 trajectory，用组内 reward 均值和标准差做相对优势：

```text
A_i = (R_i - mean_group) / (std_group + epsilon)
```

为什么本项目更适合 GRPO：

- 工具调用、金融问答、数学推理很多任务只有最终答案级分数。
- 训练 critic 的显存和工程复杂度较高，且中间状态 value label 很难稳定。
- GRPO 能把显存留给 rollout、长上下文和 vLLM KV cache。

边界：

- GRPO 信用分配比 critic / process reward 更粗，无法精确定位哪一步工具调用错了。
- 如果同组样本全对或全错，reward 方差小，优势信号会弱。
- 不要说 GRPO 永远优于 PPO；更稳表述是“更适合当前 outcome-level reward 和显存敏感的 Agent 任务”。

#### 3.5.2 SFT 冷启动

SFT 冷启动先教模型“会不会按协议做工具调用”，RL 再优化“什么时候调、调什么、调几次、调完怎么用”。直接 RL 会浪费大量预算探索工具标签、工具结果格式和多轮交互模式。

口径：

- SFT 学工具调用格式、system prompt、工具标签、工具结果和多轮回复。
- RL 优化工具调用策略和最终结果质量。
- 文档中提到约 `54K agentic SFT` 数据，建议标为需进一步核查的数据口径，不要在压力面中作为硬结论主动强调。

#### 3.5.3 KL、Mask 与 Advantage 归一化

- KL 用来限制当前策略不要偏离参考策略太远，防止 reward hacking、格式漂移和过度工具调用。
- KL 与 entropy 不同：KL 衡量新旧策略或参考策略之间的分布差异，entropy 衡量单个策略在某个位置的不确定性。
- response_mask / loss_mask 用于只在模型生成的有效 token 上计算 loss，排除 padding 和外部工具返回内容。
- 工具返回不是模型动作，通常不作为 policy action 训练，否则模型会被错误训练成“生成工具结果”。
- DataProto 要保留 uid，避免 sequence balancing 或 batch reorder 后丢失同 prompt 分组。

#### 3.5.4 为什么需要熵

熵衡量模型在某个 token 位置有多不确定：

```text
H = -sum p log p
```

工具调用场景中，工具返回、搜索摘要、Python 输出和分支选择会让模型面对新信息，这些位置往往高熵，也更可能影响后续决策。熵机制不是奖励随机性，而是把“不确定且可能关键的位置”纳入采样预算和训练权重控制。

压力面回答：

> 高熵不等于高价值。高熵只说明模型不确定，可能是关键决策点，也可能只是混乱。项目使用熵，是在已有 reward 和策略约束下辅助分配学习信号，而不是让模型无限随机探索。

#### 3.5.5 AEARPO 与 ARAEPO 的统一口径

文档中存在 AEARPO / ARAEPO 命名演进。统一口径：

- AEARPO 和 ARAEPO 都属于面向 Agent RL 的熵平衡优化系列。
- AEARPO 更侧重 rollout、工具调用和分支采样效率。
- ARAEPO 更强调 policy update 阶段的 entropy-aware advantage 和稳定性机制。
- 不要把它们讲成完全无关的两个项目，也不要硬编一个没有冲突的命名故事。

#### 3.5.6 Entropy-Aware Advantage

可确认核心机制：

```text
A' = A * (1 + alpha * z_H)
z_H = (H - mean(H)) / std(H)
```

其中 `alpha` 常见口径为 `0.2`，应解释为经验超参，不是理论最优。`detach()` 表示熵只作为权重调节信号，不让熵标准化本身引入额外梯度路径。

回答边界：

- 直接使用 token entropy 的明确机制是 entropy-aware advantage。
- 不要说高熵 token 一定被固定放大到 1.2 倍，标准化值随 batch 变化。
- 如果被问 ablation，诚实说明完整拆分实验仍需补充。

#### 3.5.7 Dynamic Rollout 与分支采样

Dynamic Rollout 的目标是更聪明地分配采样预算，而不是每个 prompt 固定生成同样多轨迹。项目支持 `initial_rollouts`、`rollout n`、`beam_size`、`branch_probability` 等参数，让仍然活跃、可能有信息增益的轨迹 fork 出分支继续探索。

统一口径：

- 机制目的：提高有效探索、减少无效重复调用、让高不确定性位置有更多候选轨迹。
- 成本控制：必须配合工具去重、缓存、循环检测、call limit、timeout 和监控。
- 不要把 Dynamic Rollout 说成已经证明最优的采样策略。
- 不同文档对分支概率细节表述不完全一致，具体公式以实际训练配置为准。

#### 3.5.8 熵相关 clipping 与 Dual-Clip

稳妥口径：

- 项目有熵相关的 policy update 稳定机制，会与 entropy-aware advantage、PPO ratio clipping、dual-clip 组合使用。
- 不应说成“clip 上下界直接由 entropy 数值逐 token 决定”。
- Dual-Clip 用于限制负 advantage 样本导致的过度惩罚，降低训练不稳定风险。
- NaN / loss spike 需要结合 entropy std 兜底、grad norm 裁剪、finite 检测、KL、mask、dynamic micro batch 和 checkpoint resume 处理。

### 3.6 金融场景中的任务流程

`project_id: FIN_AGENTIC_RL_ARPO`

#### 3.6.1 为什么选择金融经济

金融经济任务适合检验 Agent 能力，因为它既有宏观政策解释、财务报表分析、公司估值、投资组合、金融数学、监管合规，也有数值计算、多步推理、公式选择和领域规则。它不是为了说明模型可以直接做投资决策，而是作为复杂任务验证样本。

#### 3.6.2 金融数据构建

金融经济数据覆盖 8 个子领域，总计 `4239` 条 QA：

| 子领域 | QA 数量 | 能力特点 |
|---|---:|---|
| 宏观经济与政策 | 747 | 概念、因果解释、政策理解 |
| 投资与组合管理 | 681 | 风险收益、组合、矩阵和指标 |
| 公司金融与估值 | 679 | WACC、NPV、估值建模 |
| 银行与货币市场 | 610 | 利率、久期、货币市场 |
| 微观经济学 | 560 | 供需、弹性、均衡 |
| 金融数学 | 374 | 衍生品、公式、多步计算 |
| 财务报表分析 | 329 | 财报结构化分析 |
| 金融监管与合规 | 259 | 条款、规则、边界条件 |

重要口径：

- 总 QA `4239` 是领域构建总量，不等于训练集行数。
- `finance_train.parquet` 为 `3391` 行、5 列。
- `finance_valid.parquet` 为 `508` 行。
- 字段包括 `data_source`、`prompt`、`ability`、`reward_model`、`extra_info`。
- `train_10k.parquet` 为 `10000` 行，`hard_search_1k.parquet` 实际为 `1071` 行。

#### 3.6.3 Parquet schema 与 reward_model

`finance_train.parquet` 的 5 列：

- `data_source`：数据来源。
- `prompt`：角色对话列表或模型输入。
- `ability`：金融子领域或任务能力类别。
- `reward_model`：rule 风格、ground truth 或答案校验口径。
- `extra_info`：split、domain、difficulty 等元信息。

schema 的价值是让金融任务直接进入现有 RL 数据流。DataLoader 读取 prompt，reward 计算读取 ground truth，extra_info 支持按领域和难度分析。

边界：

- `reward_model` 中可能包含完整分步答案，有助于未来步骤级评分。
- 当前主口径仍是 outcome-level / rule-based / 数值容差 / F1 / 关键点匹配，不能说已经实现成熟过程奖励。

#### 3.6.4 三层金融评估与结果

金融评估三层结构：

| 评估层 | 题量 | 作用 |
|---|---:|---|
| finance 综合评估 | 340 | 看整体金融经济能力 |
| FinBench 高难基准 | 200 | 看高难推理上限 |
| 8 个领域专项 | 8 × 60 = 480 | 定位细粒度领域短板 |
| 合计 | 1020 | 综合、难度、领域三维诊断 |

统一结果口径：

- 金融综合：`77.6%`
- FinBench 高难：`45.5%`
- 8 领域专项平均：`73.8%`
- 难度拆分：easy `89.4%`，medium `76.2%`，hard `58.7%`
- 领域拆分：宏观经济与政策 `82.1%`，财务报表分析 `79.5%`，公司金融与估值 `77.8%`，投资与组合管理 `71.3%`，微观经济学 `70.5%`，银行与货币市场 `66.2%`，金融数学 `63.4%`，金融监管与合规 `59.8%`

解释口径：

- 基础计算、公式明确、结构化任务表现更好。
- 监管合规、金融数学、高难估值、Monte Carlo 和复杂多步任务是短板。
- `45.5%` 不要包装成强结果，它暴露了高难场景边界。
- `77.6%` 是当前构建评估集的统一口径，不等于真实金融生产能力或投资建议能力。

### 3.7 核心技术方案

`project_id: FIN_AGENTIC_RL_ARPO`

#### 3.7.1 ToolAgent 状态机

vLLM 是高吞吐推理引擎，不管理完整多轮工具状态。项目在 vLLM 外层封装 ToolAgent：

1. 模型生成到工具停止标签。
2. ToolAgent 解析工具名和参数。
3. 调用搜索或 Python 等工具。
4. 将工具结果包装后拼回上下文。
5. 继续生成，直到 EOS、长度上限、call limit 或循环终止。

状态机要追踪：

- 当前输入、初始 prompt、active indices、dones。
- 工具调用次数、工具历史、重复调用 hash。
- result mask / loss mask，避免把工具返回当成模型动作训练。
- 超时、错误、重试和终止状态。

#### 3.7.2 搜索工具与 Python 工具

搜索工具：

- 通过搜索标签触发，调用外部搜索 API，返回摘要进入上下文。
- 需要缓存、并发控制、超时、重试、结果长度限制和 API key 保护。
- 缓存和去重可以减少重复搜索、降低成本和提升复现性。

Python 工具：

- 通过代码标签触发，用指定 conda 环境的 Python 子进程执行代码，返回 stdout 或错误信息。
- 适合数学计算、矩阵运算和未来金融建模。
- 当前更准确地说是“子进程执行 + timeout”，不能夸大为生产级安全沙箱。
- 生产化需要容器或微虚拟机隔离、CPU/内存/时间限制、网络限制、文件系统权限、依赖白名单和审计日志。

#### 3.7.3 去重、循环检测、重试和监控

工具稳定性机制：

- 去重：用工具名和内容 hash 识别重复请求，复用结果，减少 API 调用和重复计算。
- 循环检测：连续多次调用同一工具且 query 相似时终止轨迹。
- 指数退避：外部 API 失败时按递增延迟有限重试。
- call limit：限制工具调用最大步数。
- timeout：限制单次工具执行时长。
- metrics：记录工具调用总数、成功率、失败数、平均执行时间、最大重试、去重次数、循环终止、branch 来源、unique queries。

待确认数字：

- API 调用降低 `15-30%`、工具调用频率降低约 `50%`、GAIA `61.2% Pass@5` 都只能作为待确认或经验观察，不能主动当硬结果。

#### 3.7.4 Ray、vLLM、FSDP 与 HybridEngine

- Ray 管理分布式 worker 和 GPU 资源，把 ActorRollout、Critic、RefPolicy、RewardModel 等角色映射到不同 WorkerGroup。
- GRPO 场景通常不启用 critic，PPO / GAE 场景才会启用 value worker。
- vLLM 负责高吞吐 rollout。
- FSDP 负责训练和梯度同步。
- HybridEngine 在生成阶段使用 vLLM 和 KV cache，在训练阶段切回 FSDP 做 log_prob、loss 和 optimizer step。
- `gpu_memory_utilization` 过高会挤占训练显存，过低会降低 rollout 吞吐，需要结合 batch、序列长度和模型大小调。

#### 3.7.5 Sequence Balancing 与 Dynamic Micro Batch

Agent trajectory 长度差异大：有的样本不调工具很短，有的多轮搜索和 Python 计算很长。训练负载主要由 token 数决定，而不是样本数。

- Sequence balancing：按有效 token 数重排 batch，让不同 GPU 负载更均衡。
- Dynamic micro batch：按每 GPU 最大 token 数切分，长样本少放、短样本多放，减少 OOM 和显存浪费。
- 关键风险：重排后必须保留 uid、mask 和 meta_info，否则 GRPO 分组和 loss 计算会错。

#### 3.7.6 DataProto 数据协议

DataProto 是跨模块传递训练数据的统一协议：

- `batch`：TensorDict，如 `input_ids`、`attention_mask`、`responses`、`old_log_probs`、`advantages`。
- `non_tensor_batch`：uid、raw prompt、extra_info 等非 tensor 信息。
- `meta_info`：temperature、micro_batch_size、max_token_len 等运行时参数。

价值：

- 支持切片、concat、repeat、reorder 和分布式传输。
- 同一个 prompt 生成 n 条 response 后，需要 repeat 原 prompt 并保留 uid，才能做 GRPO 组内 advantage。

#### 3.7.7 Checkpoint 与部署转换

checkpoint 需要保存 actor 参数、可选 critic 参数、优化器状态、dataloader 状态和 global step。恢复训练不能只加载模型，还要恢复 dataloader，否则数据顺序可能改变。

FSDP checkpoint 是分片格式，通常不能直接给 vLLM 部署，需要先合并转换成 HuggingFace 格式，再检查 tokenizer、config 和 chat template。

#### 3.7.8 Sync 与 Async Rollout

- Sync rollout：生成完一批轨迹后再训练，流程简单、稳定、容易调试。
- Async rollout：让生成和训练更并行，通过异步管理 vLLM 服务 wake / sleep，减少 GPU 空闲。
- Async 有吞吐潜力，但会带来策略版本、log_prob、reward、batch 对齐和工具状态同步问题。
- 稳妥口径：复现实验和 debug 优先 sync，系统稳定后再考虑 async 提吞吐。

### 3.8 难点与解决方案

`project_id: FIN_AGENTIC_RL_ARPO`

| 难点 | 具体表现 | 解决方案 | 面试口径 |
|---|---|---|---|
| Outcome reward 信用分配粗 | 只知道整条轨迹对错，不知道哪一步贡献最大 | GRPO 组内相对 advantage、工具日志、错误分析、未来过程奖励 | 承认 GRPO 简化系统复杂度，但不完全解决 token 级归因 |
| 工具调用高熵与长轨迹 | 工具返回后决策不确定，普通 token 稀释关键信号 | entropy-aware advantage、KL、clip、dual-clip、mask | 熵是辅助不确定性信号，不是正确性标签 |
| 分支采样成本高 | 多条 trajectory、多次搜索/Python 调用放大成本 | Dynamic Rollout、去重、缓存、call limit、timeout、循环检测 | 探索必须受成本和稳定性约束 |
| vLLM/FSDP 显存切换 | rollout KV cache 与训练显存互相挤占 | HybridEngine、`gpu_memory_utilization` 调参、dynamic micro batch | vLLM 是推理引擎，FSDP 是训练更新，两者需要协调 |
| 长短序列负载不均 | GPU 按样本数分配会等待或 OOM | sequence balancing、dynamic micro batch、保留 uid/mask | token 数比样本数更决定训练负载 |
| 金融数据泛化 | 自建数据可能模板过拟合，真实业务多样性不足 | 8 领域覆盖、训练/验证切分、三层评估、held-out 模板、未来公开数据 | 生成数据是 Phase 1，不是最终金融智能全部来源 |
| 评估可靠性 | rule-based 对开放答案和概念题有限 | 数值容差、F1、关键点匹配、未来 LLM-as-judge / 人工抽样 | 计算题更可靠，概念题要谨慎 |
| 工具安全 | Python 子进程不是强沙箱，搜索 API 有凭证风险 | timeout、环境变量、缓存、生产容器隔离、审计 | 当前是训练研究环境，不要说生产级安全沙箱 |

### 3.9 工程实现细节

`project_id: FIN_AGENTIC_RL_ARPO`

#### 3.9.1 训练链路可口述实现

不展示源码时，用模块边界和数据流说明：

> 配置先加载模型、数据、工具和算法开关；DataLoader 读取 Parquet，构造 DataProto；Ray 初始化不同 worker；vLLM 生成 rollout；ToolAgent 在生成过程中暂停、解析工具、调用搜索或 Python、把结果写回上下文；reward manager 根据 reward_model 和 ground truth 打分；GRPO 计算组内 advantage；再结合 entropy-aware advantage、mask、KL、clipping 做 policy update；FSDP 更新 actor；最后保存 checkpoint 并合并为 HF 格式部署评估。

#### 3.9.2 关键状态与排障点

- ToolAgent：active samples、call counters、dones、工具历史、result mask。
- DataProto：uid、attention mask、response mask、extra_info、meta_info。
- 训练稳定：reward、KL、entropy、clipfrac、grad_norm、loss、tool success rate。
- 工具排障：timeout、retry、缓存命中、loop termination、API key、搜索失败。
- 分布式排障：OOM、sequence imbalance、dataloader resume、FSDP checkpoint merge、tokenizer / chat template 不一致。

#### 3.9.3 金融训练和评估闭环

- 训练数据：`finance_train.parquet` 3391 行。
- 验证数据：`finance_valid.parquet` 508 行。
- 评估集：finance 综合 340、FinBench 200、8 领域专项 480，总计 1020。
- 结果输出：综合、难度、领域三维结果。
- 错误分析：监管合规、金融数学、hard 题、高难估值和复杂计算。

### 3.10 面试高频问题与回答口径

`project_id: FIN_AGENTIC_RL_ARPO`

#### Q1：用一句话介绍项目。

回答：

> 这是一个面向工具调用 LLM Agent 的强化学习训练项目，基于 verl、Ray、vLLM 和 FSDP，让模型更稳定地进行搜索、Python 计算和多轮推理。核心问题是 Agent 轨迹里的工具返回、长序列和高熵 token 会让训练不稳定，所以项目围绕 AEARPO / ARAEPO 做熵平衡、工具稳定性和金融经济评估。

#### Q2：为什么用 GRPO 而不是 PPO？

回答：

> 不是 PPO 不好，而是这个任务更偏 outcome-level reward。工具调用轨迹很长，中间状态 value label 很难稳定，训练 critic 成本高且占显存。GRPO 用同一 prompt 多条 trajectory 的组内 reward 做相对 advantage，更轻量，适合最终答案可验证、显存敏感的 Agent 任务。但我也承认它信用分配更粗。

#### Q3：SFT 和 RL 分别学什么？

回答：

> SFT 先学工具调用协议和多轮交互格式，比如什么时候输出工具标签、如何接收工具结果。RL 再根据 reward 优化策略，也就是什么时候调工具、调什么、调完怎么利用结果。如果直接 RL，会把很多预算浪费在学工具格式上。

#### Q4：为什么需要熵机制？

回答：

> 工具返回后，模型面对新信息，很多关键决策点会变得高熵。普通 GRPO 如果对所有 token 一视同仁，关键信号可能被长序列模板 token 稀释。熵机制不是奖励随机性，而是用不确定性辅助分配采样预算和 advantage 权重，同时用 KL、clip、call limit 等控制过探索。

#### Q5：AEARPO 和 ARAEPO 有什么区别？

回答：

> 稳妥讲法是它们属于同一条 Agent RL 熵平衡优化演进线。AEARPO 更偏 rollout、工具调用和分支采样效率；ARAEPO 更偏 policy update 阶段的 entropy-aware advantage 和稳定性机制。不要把它们说成完全无关的两个项目。

#### Q6：vLLM 为什么不能直接做完整 Agent？

回答：

> vLLM 是高吞吐推理引擎，它负责生成 token，但不负责工具状态、工具重试、循环检测、reward、advantage 和 policy update。完整 Agent 还需要 ToolAgent 管多轮工具交互，训练框架管 reward 和 FSDP 更新。

#### Q7：金融数据怎么构建？

回答：

> 金融经济覆盖 8 个子领域，总计 4239 条 QA；训练集 finance_train.parquet 是 3391 行，验证集 508 行。数据字段包含 data_source、prompt、ability、reward_model、extra_info，方便进入 verl 的 RL 管线并按领域、难度评估。

#### Q8：金融结果是多少，怎么解释？

回答：

> 统一口径是金融综合 77.6%，FinBench 高难 45.5%，8 领域专项平均 73.8%。easy 89.4%、medium 76.2%、hard 58.7%。这说明模型在公式固定、计算明确的任务上较好，但高难金融数学、监管合规和复杂估值仍是短板。这个结果不能等同真实金融生产能力。

#### Q9：是不是只是复现？

回答：

> 底座确实基于 verl、Ray、vLLM、FSDP 和已有 PPO/GRPO 生态，我不会说从零造轮子。我的增量在于把 Agent RL 的工具调用稳定性、熵机制口径、金融数据 schema、reward、三层评估和训练部署闭环串起来，解决具体 Agent 和金融任务中的适配、扩展和验证问题。

#### Q10：没有完整 ablation 怎么回答？

回答：

> 我会诚实说当前能确认的是机制接入、训练链路和金融评估口径，严格论文级 ablation 还需要补充。后续可以固定数据、模型和 seed，逐个比较 baseline GRPO、entropy-aware advantage、Dynamic Rollout、工具去重和循环检测，分别看 reward、工具调用次数、token 成本、KL、稳定性和领域评估。

### 3.11 可能追问与应对

`project_id: FIN_AGENTIC_RL_ARPO`

- 追问：GRPO 没有 critic 怎么信用分配？
  - 应对：承认更粗，主要通过同 prompt 多 trajectory 的相对 reward 判断哪条轨迹整体更好；可以用过程 reward、step verifier 或 critic 对照增强，但成本更高。
- 追问：高熵 token 是否等于高价值 token？
  - 应对：不是。高熵只是模型不确定，可能关键也可能是噪声。项目把它作为启发式调节信号，仍由 reward、KL、clip 和 mask 约束。
- 追问：熵机制会不会鼓励无效探索？
  - 应对：有风险，所以不是单独最大化 entropy，而是调节 advantage，并配合 branch 上限、call limit、KL、clip、去重和循环检测。
- 追问：Python 工具安全吗？
  - 应对：当前是子进程加 timeout，不是生产级强沙箱。生产需要容器或微虚拟机、网络限制、资源配额、文件路径限制和审计。
- 追问：自建金融数据会不会模板过拟合？
  - 应对：承认风险。当前是 Phase 1，用可控数据跑通 schema、reward 和评估闭环；后续需要公开数据、真实财报、中文金融数据、held-out 模板和人工抽样。
- 追问：评估可靠吗？
  - 应对：计算题用数值容差相对可靠，概念题 F1 / 关键点匹配有局限。`77.6%` 是当前评估集统一口径，不是专家审计或生产能力。
- 追问：FinBench 只有 45.5%，是不是失败？
  - 应对：不是失败，而是高难金融任务短板暴露。它说明系统基础能力有提升空间，后续应补高难数据、Python/pandas 工具、过程校验和法规知识检索。

### 3.12 口语化回答模板

`project_id: FIN_AGENTIC_RL_ARPO`

#### 30 秒模板

我这个项目做的是 LLM Agent 的强化学习训练。底层基于 verl，用 Ray 管分布式资源，vLLM 做 rollout，FSDP 做策略更新。上层让模型在推理过程中调用搜索和 Python 工具。我的重点是处理工具调用带来的高熵、长轨迹、工具失败和分布式训练稳定性，并把训练评估扩展到金融经济场景。

#### 1 分钟模板

项目可以理解为一个面向工具调用 Agent 的 RL 训练系统。SFT 先让模型学会工具协议和多轮格式，RL 再优化工具调用策略。因为任务多是最终答案级 reward，所以项目更偏 GRPO，用同一 prompt 多条轨迹做相对 advantage。工具调用会引入高熵 token、长序列和外部失败，所以我关注 AEARPO / ARAEPO 的熵平衡机制，以及 ToolAgent 的去重、循环检测、重试和监控。系统上用 Ray、vLLM、FSDP、DataProto 跑分布式训练，领域上构建金融 8 子领域数据和 1020 题评估，统一金融综合结果是 77.6%。

#### 3 分钟模板

我会按“问题、方法、工程、领域扩展、结果和反思”讲。问题是工具型 Agent 的 RL 比普通问答难，因为轨迹长、工具返回不确定、reward 多是最终答案级。方法上先用 SFT 冷启动工具协议，再用 GRPO 做 outcome reward 优化，并通过 entropy-aware advantage 和分支采样思路处理高不确定性位置。工程上，vLLM 只负责高吞吐生成，ToolAgent 管工具状态机，Ray 管 worker 和资源，FSDP 做大模型更新，DataProto 保证 tensor 和非 tensor 信息在各阶段传递。金融扩展覆盖 8 个子领域，评估分综合、高难和领域专项。结果上综合 77.6%，但高难 FinBench 45.5%，说明复杂金融数学、监管合规和多步估值仍是短板。

#### 压力面模板

我不会把这个项目说成从零发明了强化学习框架。底座是成熟开源生态，我做的是面向工具调用 Agent 和金融任务的适配与工程闭环。对于未完整消融的机制，我会标成待验证；对于实时行情、LLM-as-judge、pandas 财务建模和生产级 Python 沙箱，我会明确说是后续方向，不会讲成已完成成果。

### 3.13 项目亮点

`project_id: FIN_AGENTIC_RL_ARPO`

- 打通 SFT、Agentic RL、多工具 rollout、reward、policy update、checkpoint、部署和评估闭环。
- 将工具调用场景中的高熵、长轨迹、分支采样和训练稳定性作为核心问题，而不是只跑通普通 SFT。
- 明确 AEARPO / ARAEPO 的统一口径，避免命名冲突。
- ToolAgent 状态机补足 vLLM 不管理工具状态的问题，支持工具暂停、解析、执行、回填和继续生成。
- 工具稳定性机制完整：去重、循环检测、指数退避、timeout、缓存、call limit、metrics。
- 分布式工程细节扎实：Ray WorkerGroup、ResourcePool、vLLM/FSDP HybridEngine、sequence balancing、dynamic micro batch、DataProto、checkpoint merge。
- 金融经济数据和评估体系较完整：8 子领域、4239 QA、3391 训练行、508 验证行、1020 题三层评估。
- 事实边界清楚：confirmed、to_verify、future_direction 分开，避免面试中过度包装。

### 3.14 风险点、边界与可改进方向

`project_id: FIN_AGENTIC_RL_ARPO`

#### 已确认事实

- 项目主体路径口径：`ae-ARPO/`。
- `finance_train.parquet`：3391 行、5 列。
- `finance_valid.parquet`：508 行。
- `train_10k.parquet`：10000 行。
- `hard_search_1k.parquet`：实际 1071 行。
- 金融评估：340 + 200 + 8 × 60 = 1020 题。
- 金融综合 77.6%，FinBench 45.5%，8 领域平均 73.8%。
- 金融 8 领域总 QA 4239 条。

#### 待确认或不建议夸大

- GAIA `61.2% Pass@5`。
- 工具调用频率降低约 `50%`。
- API 调用降低 `15-30%`。
- 每个熵机制的独立收益和完整 ablation。
- Dynamic Rollout 的稳定提升。
- `54K agentic SFT` 数据来源细节。

这些可以说成“文档中有观察或口径，但我不作为主结果主动宣传”，不能说成 confirmed。

#### future_direction，不能说成已完成

- LLM-as-judge 作为主评估机制。
- 实时行情搜索、实时监管政策检索。
- pandas 财务建模、多轮金融工具任务。
- 公开金融数据大规模导入、中文金融数据扩展。
- 生产级 Python 安全沙箱。
- 金融专用 reward、步骤级 reward、process reward。

#### 可改进方向

- 补严格 ablation：baseline GRPO、entropy-aware advantage、Dynamic Rollout、工具去重、循环检测、不同熵权重、PPO/GRPO 对照。
- 增强金融数据真实性：公开金融数据、真实财报、中文金融市场数据、held-out 模板、人工抽样。
- 增强评估：LLM-as-judge、judge rubric、多评估器一致性、bootstrap 置信区间、错误类型分析。
- 增强高难能力：金融数学、监管合规、高难估值、Monte Carlo、复杂公式和过程校验。
- 增强工具安全：容器隔离、网络限制、资源配额、文件系统白名单、审计日志。

### 3.15 检索标签

`project_id: FIN_AGENTIC_RL_ARPO`

```text
include_keywords:
FIN-Agentic_RL, ae-ARPO, AEARPO, ARAEPO, Agentic RL, LLM Agent强化学习, GRPO, PPO, SFT, RLHF, outcome reward, reward_model, advantage, KL, entropy, 熵平衡, Entropy-Aware Advantage, Dynamic Rollout, Dual-Clip, ToolAgent, tool calling training, 搜索工具, Python工具, dedup, loop detection, retry, Ray, WorkerGroup, ResourcePool, vLLM, FSDP, HybridEngine, DataProto, TensorDict, sequence balancing, dynamic micro batch, checkpoint, HuggingFace转换, finance_train, finance_valid, FinBench, 77.6, 45.5, 73.8, 1020题, 4239 QA, 金融经济, 金融数学, 金融监管

exclude_keywords:
DATA_ENGINEER_AGENT, data_engineer, 企业级数据工程Agent, NL2SQL, Schema Linking, SQLGlot, LanceDB, 指标口径治理, 参考SQL, 数据管道, ETL, 调度, 数据质量, MCP企业工具平台, Skills插件体系, 企业数据查询

trigger_questions:
为什么用GRPO不用PPO, AEARPO和ARAEPO区别, 熵机制怎么做, 高熵是不是高价值, ToolAgent怎么工作, vLLM为什么不能直接做Agent, Ray/vLLM/FSDP怎么协同, finance数据怎么构建, 77.6%怎么评估, FinBench为什么低, 没有ablation怎么回答, Python工具安全吗
```

## 4. 跨项目对比与防混淆说明

| 对比项 | `DATA_ENGINEER_AGENT` | `FIN_AGENTIC_RL_ARPO` | 防混淆规则 |
|---|---|---|---|
| 业务场景 | 企业数据分析、自然语言查数、半导体生产/良率/经营数据、指标口径 | 工具调用 LLM Agent 强化学习、金融经济任务训练与评估 | 问“查数据、写 SQL、schema、指标”走数据工程；问“训练、RL、金融评估”走 FIN |
| 技术关键词 | NL2SQL、Schema Linking、RAG、参考 SQL、MCP、Skills、Workflow、SQLGlot、LanceDB、权限治理 | GRPO、PPO、SFT、Reward、KL、熵、AEARPO、ARAEPO、ToolAgent、Ray、vLLM、FSDP、DataProto | 出现 GRPO/Ray/vLLM 不要召回数据工程；出现 SQL/schema 不要召回 Agentic RL |
| Agent 类型 | 企业数据工程 Runtime，Workflow + 局部 Agentic Node | LLM Agent RL 训练系统，ToolAgent + rollout + policy update | 数据工程项目回答“如何执行任务”；FIN 项目回答“如何训练模型” |
| 数据来源 | 表结构、字段说明、样例值、业务文档、指标定义、参考 SQL、平台文档 | Parquet / JSONL 训练评估数据、金融 QA、reward_model、工具轨迹 | “字段/表/指标”属于数据工程；“trajectory/reward/Parquet训练数据”属于 FIN |
| 主要优化目标 | SQL 可执行性、语义正确性、检索命中、权限可控、交付复用 | Agent 训练稳定性、工具调用策略、rollout 效率、金融评估表现 | 不要把 SQL 成功率说成 RL reward，不要把 77.6% 说成 NL2SQL 准确率 |
| 面试官词触发 | `data_engineer`、企业级、NL2SQL、SQL、schema、ETL、调度、数据质量、MCP、Skills | FIN、金融、Agentic RL、ARPO、GRPO、PPO、熵、Ray、vLLM、FSDP、FinBench | 先按强关键词路由，再看语义 |
| 容易混淆的问题 | “Agent 工具调用怎么做”“RAG 怎么用”“评估怎么做” | “Agent 工具调用怎么做”“评估怎么做”“Python 工具安全吗” | 工具调用在数据工程里服务 SQL 查询；在 FIN 里服务训练 rollout |
| 如何避免混合回答 | 每个回答开头隐式或显式确认项目，如“在企业数据工程 Agent 里...” | 每个回答开头隐式或显式确认项目，如“在 FIN-Agentic RL 项目里...” | 如果检索结果跨项目，先丢弃不匹配 `project_id` 的 chunk |

### 4.1 常见混淆示例

- 问：“你的 Agent 怎么调用工具？”
  - 若上下文是 SQL、schema、数据查询，应答 `DATA_ENGINEER_AGENT`：数据库、文档、参考 SQL、日期、MCP、Skills 工具，重点是权限和执行验证。
  - 若上下文是 RL、训练、rollout、金融，应答 `FIN_AGENTIC_RL_ARPO`：ToolAgent、搜索、Python、去重、循环检测、reward、mask。
- 问：“你怎么评估效果？”
  - 数据工程项目：Top-K 命中、Schema Linking、SQL 执行成功率、结果正确率、延迟、token 成本。
  - FIN 项目：reward、金融综合 77.6%、FinBench 45.5%、领域专项 73.8%、KL、entropy、工具成功率。
- 问：“RAG 在项目中有什么作用？”
  - 数据工程项目：RAG 是 SQL 生成上下文约束层。
  - FIN 项目：原文主要是搜索工具和金融数据，不要把数据工程 RAG 架构套过去。
- 问：“Python 工具安全吗？”
  - 数据工程项目：可回答工具权限治理、脚本调用分级、敏感路径隔离。
  - FIN 项目：当前是 conda 子进程 + timeout，不是生产级沙箱。

## 5. Agent 检索与回答约束

### 5.1 检索前置规则

1. 回答前必须先判断 `project_id`。
2. 如果问题包含明确项目名、路径、业务场景或技术强关键词，直接路由到对应项目。
3. 如果问题没有项目指向，先问澄清问题，不要混合回答。
4. 如果检索结果来自两个项目，先按问题关键词和排除关键词重排，只保留同一 `project_id` 内容。
5. 如果一个问题确实要求跨项目对比，必须显式分段，分别写 `DATA_ENGINEER_AGENT` 和 `FIN_AGENTIC_RL_ARPO`，不能合成一个项目经历。

### 5.2 禁止混用规则

- 禁止把 `FIN_AGENTIC_RL_ARPO` 的 GRPO、PPO、熵机制、Ray、vLLM、FSDP、FinBench、77.6% 套到 `DATA_ENGINEER_AGENT`。
- 禁止把 `DATA_ENGINEER_AGENT` 的 NL2SQL、Schema Linking、参考 SQL、MCP/Skills 企业工具治理、数据管道、ETL、调度、指标口径治理套到 `FIN_AGENTIC_RL_ARPO`。
- 禁止把 FIN 项目的 `77.6%` 说成数据工程项目 SQL 准确率。
- 禁止把数据工程项目固定 benchmark 的检索 F1 / Top-5 说成 FIN 项目训练收益。
- 禁止把两个项目的工具调用混在一起：数据工程工具服务 SQL 查询和企业执行安全；FIN 工具服务训练 rollout 和 Agent RL 轨迹。
- 禁止把 future_direction 说成 confirmed。

### 5.3 回答生成规则

- 项目介绍类问题：优先使用对应项目的 30 秒 / 1 分钟模板。
- 技术深挖类问题：优先使用“核心技术方案”和“难点与解决方案”。
- 压力面问题：必须参考“风险点、边界与可改进方向”和第 6 节冲突表。
- 数字类问题：只使用 confirmed 数字，并明确口径。to_verify 数字除非面试官主动问，否则不主动报。
- 生产化类问题：用“具备生产化基础 + 真实上线需权限审计配套”的稳妥表达。
- 安全类问题：不要输出任何密钥、连接串、真实账号、内部路径和敏感配置。

### 5.4 简单路由伪逻辑

```text
if query contains [NL2SQL, SQL, Schema Linking, data_engineer, ETL, 调度, 数据质量, MCP, Skills, 数据查询]:
    route = DATA_ENGINEER_AGENT
elif query contains [FIN, 金融, Agentic RL, GRPO, PPO, AEARPO, ARAEPO, 熵, Ray, vLLM, FSDP, FinBench]:
    route = FIN_AGENTIC_RL_ARPO
elif query asks explicit comparison:
    answer both projects in separated sections
else:
    ask clarification before answering
```

## 6. 原始来源映射

### 6.1 合并章节来源表

| 合并章节 | 主要来源文件 | 合并说明 |
|---|---|---|
| 0. 使用说明与检索规则 | 四份项目知识库 + 两份简历 | 新增跨项目路由规则，解决直接上传多文件导致的项目混召回问题 |
| 1. 项目索引与检索路由表 | 四份项目知识库 + 简历技术关键词 | 新增 project_id、别名、核心关键词、排除关键词 |
| 2.1-2.3 数据工程定位、背景、目标 | `企业级数据工程 Agent_claudecode整理版.md`、`企业级数据工程 Agent_codex整理版.md`、两份简历 | 合并 30 秒/1 分钟/2 分钟介绍、项目背景、职责和成果 |
| 2.4-2.6 数据工程架构、Agent 设计、链路 | 两份数据工程知识库 | 合并整体架构、Workflow / Node、Agent Runtime、GenSQL Node、NL2SQL 流程、意图路由 |
| 2.7 数据工程核心技术方案 | 两份数据工程知识库 | 合并 Schema Linking、RAG、混合检索、参考 SQL、SQL 幻觉、执行验证、多模型多数据库 |
| 2.8-2.9 数据工程难点和工程实现 | 两份数据工程知识库 + 简历技术栈 | 合并权限治理、MCP、Skills、配置化、日志、测试、生产化、大规模扩展 |
| 2.10-2.15 数据工程面试问答、模板、风险、标签 | 两份数据工程知识库 | 合并高频 Q&A、追问、口播模板、红线清单和检索标签 |
| 3.1-3.4 FIN 项目定位、背景、目标、架构 | 两份 AgentRL 知识库 + 简历项目二 | 合并开场回答、个人贡献、系统架构和训练链路 |
| 3.5 FIN RL / ARPO 设计 | 两份 AgentRL 知识库 | 合并 PPO、GRPO、SFT、KL、mask、AEARPO/ARAEPO、entropy-aware advantage、dynamic rollout、dual-clip |
| 3.6 金融任务流程 | 两份 AgentRL 知识库 + 简历项目二 | 合并金融 8 领域、Parquet schema、三层评估和结果 |
| 3.7-3.9 FIN 核心技术与工程实现 | 两份 AgentRL 知识库 | 合并 ToolAgent、搜索/Python 工具、Ray、vLLM、FSDP、DataProto、checkpoint、sync/async |
| 3.10-3.15 FIN 面试问答、模板、风险、标签 | 两份 AgentRL 知识库 | 合并压力面、事实口径、future direction 和检索标签 |
| 4. 跨项目对比与防混淆 | 新增综合章节 | 用两个项目共同关键词构建防混淆表 |
| 5. Agent 检索与回答约束 | 新增综合章节 | 把用户要求转化为可执行检索规则 |
| 6. 原始来源映射 | 所有已读文件 | 列出文件来源、冲突点、统一口径和需确认内容 |

### 6.2 文件来源细分

| 原始文件 | 项目 | 生成来源 | 主要内容 | 合并处理 |
|---|---|---|---|---|
| `企业级数据工程 Agent_claudecode整理版.md` | `DATA_ENGINEER_AGENT` | Claude Code | 42 张 KB 卡，包含项目介绍、NL2SQL、RAG、MCP、Skills、权限、工程化、评估、红线 | 保留参考 SQL、多模型多数据库、红线和固定 benchmark 谨慎口径；与 Codex 重复内容合并 |
| `企业级数据工程 Agent_codex整理版.md` | `DATA_ENGINEER_AGENT` | Codex | 40 张 KB 卡，结构更紧凑，包含架构、Schema Linking、混合检索、生产化、语义层 | 作为数据工程主结构，合并 Claude Code 的补充细节 |
| `AgentRL项目_面试私有知识库_claudecode整理版.md` | `FIN_AGENTIC_RL_ARPO` | Claude Code | chunk schema，包含金融扩展原因、8 领域、压力面、事实口径、future direction | 保留更多压力面问答和金融领域解释 |
| `AgentRL项目_面试私有知识库_codex整理版.md` | `FIN_AGENTIC_RL_ARPO` | Codex | chunk schema，包含统一事实口径、PPO/GRPO、熵机制、Agent 工程、分布式、金融结果 | 作为 FIN 主结构，合并 Claude Code 的扩展问答 |
| `AI应用开发工程师_AI-Agent工程师_简历.md` | 两个项目 | 简历原版 | 项目角色、方向、技术栈、成果 | 用于补充职责和项目定位，不作为冲突事实唯一来源 |
| `AI应用开发工程师_AI-Agent工程师_简历_优化版.md` | 两个项目 | 简历优化版 | 优化后的项目经历和技术关键词 | 用于补充面试表达、角色边界和关键词 |

### 6.3 冲突点、统一表述与需确认项

| 冲突点或风险点 | 来源文件 | 推荐统一表述 | 是否需进一步确认 |
|---|---|---|---|
| 用户说目录读 5 个文件，但实际发现 6 个 Markdown 文件 | 目录扫描 | 合并主体使用 4 份项目知识库；2 份简历作为背景参照 | 否 |
| 数据工程项目中 BM25 是否已完整实现 | 两份数据工程知识库、简历 | 可讲“向量 + FTS/关键词 + 字段加权 + 混合重排”；BM25 作为混合检索思想谨慎表达 | 如面试要说具体实现，需确认 |
| 数据工程 Web / TUI / Streamlit 交付状态 | 数据工程 Claude Code 版 | 可讲多入口包括 CLI、API、MCP、Gateway、Web / TUI；不要强称完整生产 Web / Streamlit | 需确认 |
| 数据工程固定 benchmark 数字 | 数据工程 Claude Code 版 | 检索 F1 `0.71 -> 0.89`、Top-5 `65% -> 82%`、schema 检索从秒级到百毫秒级只能说固定 benchmark / 内部测试集 | 需确认具体 benchmark |
| 数据工程百万级规模 | 两份数据工程知识库 | 作为扩展设计：分域分层索引、增量更新、缓存、粗召回 + 重排；不要说已在线承载百万级生产 | 需确认生产事实 |
| FIN 金融综合旧口径与 77.6% 冲突 | 两份 AgentRL 知识库 | 最终统一采用金融综合 `77.6%`、FinBench `45.5%`、领域平均 `73.8%`；旧低口径不采用 | 否，除非用户提供新证据 |
| AEARPO / ARAEPO 命名关系 | 两份 AgentRL 知识库 | 统一为同一条 Agent RL 熵平衡优化演进线，AEARPO 偏 rollout，ARAEPO 偏 policy update | 否 |
| 熵相关 clipping 机制表述 | 两份 AgentRL 知识库 | 可确认 token entropy 用于 entropy-aware advantage；clipping 只讲 policy update 稳定性，不能说 clip 上下界直接由 entropy 逐 token 决定 | 如需源码级细节，需确认 |
| GAIA 61.2% Pass@5、工具调用降低 50%、API 降低 15-30% | 两份 AgentRL 知识库 | 标为 to_verify 或经验观察，不作为主结果主动宣传 | 是 |
| 54K agentic SFT 数据 | AgentRL Codex 版 | 可说文档中提到约 54K，用于 SFT 冷启动；压力面中需说明来源细节待核查 | 是 |
| LLM-as-judge、实时行情、pandas 财务建模、中文金融数据 | 两份 AgentRL 知识库 | 归为 future_direction，不能说成已完成主能力 | 否 |
| Python 工具安全级别 | 两份 AgentRL 知识库 | 当前是 conda 子进程 + timeout，不是生产级安全沙箱；生产需容器/微虚拟机隔离 | 否 |

## 7. 合并说明

本合并版主要通过以下方式降低检索冲突：

- 为两个项目建立唯一 `project_id`，并在每个重要知识块中重复出现项目标识。
- 给每个项目配置核心关键词、项目别名、排除关键词和触发问题。
- 按项目强隔离，避免把两个项目混在同一个无边界章节中。
- 将 Claude Code 和 Codex 的重复内容合并为统一口径，将互补内容补入对应小节。
- 对冲突或不稳定口径标注为“需确认”“to_verify”或“future_direction”，不在正文中当硬事实夸大。
- 将跨项目容易混淆的“Agent 工具调用”“评估”“RAG”“Python 工具安全”等问题单独放入防混淆表。
- 强制 Agent 回答前先路由项目；如果无法判断项目归属，先追问，不混合回答。

