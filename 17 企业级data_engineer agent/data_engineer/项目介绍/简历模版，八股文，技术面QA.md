# 编号：15_Data_engineer-Agent_简历，八股，技术面

> 关于简历：简历中的内容都是给参考的，你自己学了多少、学得多深，就按自己需求写进简历。怎么方便面试怎么来，项目未必需要全学会，实在来不及就把你学会的部分写到简历上，灵活变通。

## 两份简洁版简历模板

### Data_engineer 项目简历

#### 项目简介

Data_engineer 是一个数据工程智能体平台，通过自然语言处理和语义检索，将用户的自然语言查询转换为准确的 SQL 语句。我基于多节点工作流编排设计并实现了整个系统，支持 10+ 种 LLM 提供者和 11 种数据库，通过持续学习构建进化的知识上下文，显著提升 SQL 生成准确率。

#### 核心功能

- 自然语言转 SQL：NL -> 意图理解 -> 语义检索 -> SQL 生成
- Evoluble Context：构建活的知识库，捕获 schema 元数据、参考 SQL、语义模型、指标
- 多数据库支持：内置 SQLite/DuckDB + PostgreSQL、MySQL、Snowflake、StarRocks 等适配器
- 多 LLM 支持：OpenAI、Claude、Gemini、DeepSeek、Qwen 等 10+ 提供者
- Subagent 封装：将成熟领域封装为 scoped chatbot，通过 API/Web/MCP 交付
- 语义层集成：通过 MetricFlow 集成定义业务指标，生成跨方言 SQL
- MCP 协议：既是 MCP Server 暴露工具，也是 MCP Client 消费外部工具

## 技术栈

| 类别 | 技术 |
| --- | --- |
| 核心框架 | Python 3.12+，OpenAI Agents SDK，LiteLLM harness，Agent-skill，SQL-RAG |
| 向量数据库 | LanceDB |
| API 服务 | FastAPI，FastMCP，MCP |
| Web UI | Streamlit |
| 测试 | pytest，ruff |
| 包管理 | uv |

## 项目简历内容

### Python/AI工程师版本

2026. 01- 2026.04 | Data_engineer 数据工程智能体 | 核心开发
**项目背景：**

数据工程师在构建 ETL 流程时面临挑战：传统方式需要手动编写大量 SQL，且难以处理跨数据库方言差异（即不同 数据库系统（如 MySQL、PostgreSQL、Oracle、SQL Server、Hive、Spark SQL 等）对 SQL 语法的实现不完全相同）。一次跨方言迁移平均需要2-3 天，且错误率高达 30%。我设计并实现了一个智能的数据工程助手，通过自然语言和语义检索，自动生成准确的 SQL 语句。

**主要负责：**

架构设计：我设计了基于多节点工作流编排的 SQL 生成系统，将查询流程分解为意图分类（BeginNode -> SelectionNode）、Schema 链接（SchemaLinkingNode）、上下文检索、LLM 生成（GenSQLAgenticNode）、执行验证（ExecuteSQLNode）、结果输出（OutputNode）等独立阶段，每个阶段由专门的 Node 节点处理，通过有向无环图（DAG）实现灵活的流程编排，支持条件分支和并行执行。架构上采用工厂模式管理节点生命周期，通过

Node.new_instance()工厂方法根据 node_type 动态创建节点，新增节点只需添加 case 分支，不破坏现有 代码，符合开闭原则。

**关键实现一向量检索系统：**我实现了基于LanceDB的向量检索系统，支持 Schema 元数据、平台文档、参考 SQL

的语义搜索。通过 create_vector_index()方法预计算向量索引（数据量小于 5000行时用IVF_FLAT，超过 时自动切换 IVF_PQ），将 Schema 检索延迟从秒级（1.2s）降低到毫秒级（120ms），降幅达 90%。向量维度采用 384 维（get_document_embedding_model），兼顾检索质量和存储开销。

**关键实现一混合检索策略：**我设计了混合检索策略（BM25+向量检索），将关键词精确匹配与语义相似度搜索结

合。通过多字段加权（vector_score × 0.5+ bm25_score × 0.3+ title_boost × 0.1+ hierarchy_boost × 0.05+ keywords_boost × 0.05）和多样性约束（DiversityScorer），显著提升检索结果的相关性和覆盖度。在 benchmark 测试集上，检索F1从 0.71 提升到 0.89，提升 25%；Top-5 准确率从 65% 提升到 82%。Query 扩展模块（QueryExpander）支持同义词扩展，进一步提升召回率 15%。

**关键实现—SQL 生成与反思：**我实现了 GenSQLAgenticNode，内部集成 Prompt 构建、LLM 调用、结果解析三

步。通过 few-shot learning 注入top_k=3个最相关的参考 SQL 示例，提升生成质量。反思机制（ReflectNode + FixNode）实现验证-分析-修复的闭环：语法错误（SQLGlot验证）、列名错误（Schema 对比）、逻辑错误 （LLM 反思）分类处理，85% 的常见语法错误可通过反思自动修复。最大反思轮次限制为 3 次，防止无限循环。

**数据建模：**我定义了 SqlTaskState 作为工作流状态载体，包含 task_id、nl_query、target_tables、generated_sql、result 等字段。Schema 信息建模 TableInfo（表名、列、描述）和 ColumnInfo（列名、类型、约束）。Context 类管理会话上下文，支持多会话并发。

**项目成果：**

- 检索准确率提升 25%：F1从 0.71 提升到 0.89，Top-5 准确率从 65% 提升到 82%
- Schema 检索延迟降低90%：从1.2s 降至120ms，支持千万级向量实时查询
- SQL 语法错误自动修复率 85%：反思机制覆盖大部分常见语法错误
- 支持 11 种数据库：PostgreSQL、MySQL、Snowflake、StarRocks、ClickHouse 等全覆盖
- LLM Token 成本降低 60%：Prompt 压缩 + 模型路由，简单查询用 GPT-4.1-mini，复杂查询用 GPT-4o

#### 技术架构

```text
用户查询 -> CLI/API -> Agent -> Workflow -> Node Graph
                                      ├─ BeginNode
                                      ├─ SchemaLinkingNode
                                      ├─ GenSQLAgenticNode
                                      │  ├─ _build_prompt()
                                      │  ├─ _retrieve_context()
                                      │  ├─ _call_llm()
                                      │  ├─ _parse_sql()
                                      │  └─ _verify_sql()
                                      ├─ ExecuteSQLNode
                                      └─ OutputNode

Storage Layer:
  LanceDB（向量） <- SchemaWithValueRAG（Schema 元数据）
                  <- DocumentStore（平台文档）
                  <- MetricRAG（业务指标）
                  <- ReferenceSqlRAG（参考 SQL）

混合检索:
  BM25（关键词） ┐
                 ├─ 加权融合 -> DiversityScorer -> Top-K
  向量（语义）   ┘
```

### STAR 法则完整示例

S（背景，15%）： 数据工程师团队每天需要编写大量 ETL SQL，传统方式依赖人工理解表结构和业务语义。平均每个查询耗时 30 分钟 以上，跨数据库方言（如 PostgreSQL -> Snowflake）的SQL 迁移需要重写，且错误率高达30%。此外，Schema 文档散落在各处，更新不及时导致生成的 SQL与实际表结构不符。 T（任务，15%）：

1. 实现自然语言到 SQL 的自动转换，减少人工编写时间
2. 构建 Schema 语义检索系统，解决表结构理解难题
3. 支持多数据库方言的SQL 生成，提升复用率
4. 建立反思验证机制，降低生成 SQL 的错误率
A（行动，50%）： 架构设计：我设计多节点工作流编排架构，将 SQL 生成流程分解为 Begin（初始化） -> selection（意图分类） ->  SchemaLinking（表结构检索） -> GenSQL（LLM 生成） -> Execute（执行验证） -> Output（结果输出）等独立节点，各节点通过 Workflow 统一调度。Workflow 管理 nodes 字典和 node_order 列表，执行时按拓扑序 调用各节点的 execute()方法。节点间通过 SqlTaskState 传递数据，不直接调用其他节点的内部状态，实现

松耦合。

**关键实现一向量检索：**我实现 SchemaWithValueRAG 存储层，基于LanceDB 向量数据库存储表结构描述。通

过 create_vector_index()创建 IVF_PQ 索引（超过5000行自动切换），将平均检索延迟从1.2s 降至 120ms。 DocumentStore 的 search_docs 方法支持多版本管理和增量更新，store_chunks 使用 delete-then-add 策略避免 merge_insert 的 commit conflict。

**关键实现一混合检索：**我设计 OptimizedRecall 类实现 BM25+向量的混合检索。通过多字段加权

（vector × 0.5 + bm25 × 0.3 + title × 0.1+ hierarchy × 0.05+ keywords × 0.05）和多样性约束，检索 F1 从 0.71提升到

0.89。Query 扩展支持同义词，将召回率进一步提升 15%。
**关键实现一反思机制：**我设计 ReflectNode 分析错误原因（语法错误/列名不存在/逻辑不合理），FixNode

针对不同错误类型调用LLM修复，HITLNode 作为兜底人工介入。GenSQLAgenticNode 的 _should_continue_reflection 方法通过 reflection_round >= 3 和 "unknown table" 等条件防止无限循环。85%的常见语法错误可通过反思自动修复。

**数据建模：**我定义 SqlTaskState 作为工作流状态载体，包含 task_id、nl_query、datasource、target_tables、

generated_sql、result 等字段。TableInfo 建模表名、列信息、描述、行数；ColumnInfo 建模列名、类型、 约束。 R（结果，20%）：

- 检索 F1 提升 25%：从 0.71到 0.89，Top-5 准确率从 65% 到 82%
- Schema 检索延迟降低90%：从1.2s到120ms，支持千万级向量实时查询
- SQL 语法错误自动修复率 85%：反思机制覆盖大部分常见语法错误
- 支持 11 种数据库：PostgreSQL、MySQL、Snowflake、StarRocks、ClickHouse 等全覆盖
- LLM Token 成本降低 60%：Prompt 压缩 + 模型路由，简单查询用小模型

### 简历要点（可复用）

1. 设计并实现基于多节点工作流编排的SQL 生成系统，将自然语言查询转换为可执行 SQL，涵盖意图分类、
- 设计并实现基于多节点工作流编排的 SQL 生成系统，将自然语言查询转换为可执行 SQL，涵盖意图分类、Schema 链接、LLM 生成、执行验证等阶段，检索 F1 提升 25%

2. 实现基于 LanceDB 的向量检索系统，通过预计算索引将 Schema 检索延迟从秒级降至毫秒级（120ms），降幅
达 90%

3. 设计混合检索策略（BM25+向量检索），通过多字段加权和多样性约束，F1 从 0.71提升到 0.89
4. 构建可扩展的存储抽象层，统一管理 Schema 元数据、业务指标、参考 SQL 等多种存储后端，通过工厂模式支持 11 种数据库适配器

5. 实现SQL 反思验证机制，85%的语法错误可通过反思自动修复

## Data_engineer 一简历写法+STAR法则指南

## 一、简历项目经历模板

### 模板 A：数据工程/NL2SQL（AI 工程师）

- 设计并实现基于多节点工作流编排的 SQL 生成系统，将自然语言查询转换为可执行 SQL，涵盖意图分类、Schema 链接、LLM 生成、执行验证等阶段

- 实现基于 LanceDB 的向量检索系统，支持 Schema 元数据、平台文档、参考 SQL 的语义搜索，预计算向量索引
将检索延迟从秒级降至毫秒级

- 设计混合检索策略（BM25+向量检索），通过多字段加权（title、hierarchy、keywords）和多样性约束，检索
F1 从 0.71 提升至 0.89

- 构建可扩展的存储抽象层，统一管理 Schema 元数据、业务指标、参考 SQL 等多种存储后端，通过工厂模式和策略模式支持 11 种数据库适配器

- 实现SQL 反思验证机制，语法错误自动修复率达 85%，减少人工介入次数

### 模板B：MCP 协议集成/工具生态

- 实现 MCP Server 暴露工具给 Claude Desktop、Cursor 等 IDE，支持一键接入 AI 辅助编程工作流
- 设计 Skills 打包工具系统，支持可配置权限管理和市场集成（agentskils.io 风格），降低用户扩展成本
- 优化 MCP 工具注册机制，支持动态加载和按需激活，减少冷启动时间 40%

### 模板C：API服务/后端架构

- 开发 FastAPI REST API 服务，支持 Chat、Agent、Database、Tool 等核心业务路由，QPS 支撑 100+
- 设计会话管理系统，基于 SQLite 本地存储实现多会话并发管理，支持会话历史导出和导入
- 实现数据库连接池管理和重试机制，支持 DuckDB、PostgreSQL、MySQL 等11 种数据库的透明切换

## 二、STAR 法则详解

#### STAR 定义表格

| 维度 | 定义 | 占比 | 说明 |
| --- | --- | --- | --- |
| S (Situation) | 背景 | 15% | 行业背景、团队痛点、技术债务 |
| T (Task) | 任务 | 15% | 目标、挑战、个人职责 |
| A (Action) | 行动 | 50% | 架构设计 -> 关键实现 -> 难点攻克 -> 数据建模 |
| R (Result) | 结果 | 20% | 量化指标、质量提升、经验沉淀 |

### STAR完整示例

S（背景，2-3句话）：数据工程团队每天需要编写大量 ETL SQL，传统方式依赖人工理解表结构和业务语义，平均 每个查询耗时 30 分钟以上，且跨数据库方言（如 PostgreSQL -> Snowflake）的 SQL 迁移需要重写。 T（任务，3-4 个目标）：

1. 实现自然语言到SQL 的自动转换，减少人工编写时间
2. 构建 Schema 语义检索系统，解决表结构理解难题
3. 支持多数据库方言的SQL 生成，提升复用率
4. 建立反思验证机制，降低生成 SQL 的错误率
A（行动，按四段展开）： 架构设计：设计多节点工作流编排架构，将SQL 生成流程分解为 Begin（初始化） -> Selection（意图分类） ->  SchemaLinking（表结构检索） -> GenSQL（LLM 生成） -> Execute（执行验证） -> Output（结果输出）等独立节点，各节点通过 Workflow 统一调度，支持条件分支和并行执行。

**关键实现：**实现 SchemaWithValueRAG 存储层，基于LanceDB 向量数据库存储表结构描述，通过预计算的

embedding 索引实现毫秒级 Schema 检索。GenSQLAgenticNode 内部集成 Prompt 构建、LLM 调用、结果解析 三步，通过 few-shot learning 注入参考 SQL 示例提升生成质量。

**难点攻克：**SQL 语法错误和逻辑错误是生成质量的主要瓶颈，通过设计反思机制——ReflectNode 分析错误原因，FixNode 按错误类型调用 LLM 修复，最大反思轮次限制为 3 次，避免无限循环。

**数据建模：**定义 SqlTaskState 作为工作流状态载体，包含 task_id、nl_query、target_tables、generated_sql、result 等字段。

R（结果，5 个量化指标）：

- 检索 F1 提升 25%：混合检索策略使 benchmark 准确率从 0.71 提升到 0.89
- Schema 检索延迟降低 90%：预计算向量索引将平均延迟从 1.2s 降至 120ms
- SQL 语法错误自动修复率 85%：反思机制覆盖大部分常见语法错误
- 支持 11 种数据库：PostgreSQL、MySQL、Snowflake、StarRocks、ClickHouse 等全覆盖
- 会话管理 100+ 并发：SQLite 本地存储支撑多用户并发会话

## 三、面试常见追问与回答策略

### Q1："这个项目的架构是怎么设计的？"

**策略：**从用户请求入口讲起，按数据流经过的模块依次展开，最后回到输出。重点讲为什么这样分层（解耦、可测试、可扩展）。

### Q2："Schema 链接具体怎么做的？"

**策略：**讲清楚向量检索的流程（query embedding  -> ANN 检索 结果解析），重点讲如何解决“表太多怎么筛"的

问题（top_k 限制+字段过滤）。

### Q3："反思机制是怎么设计的？"

**策略：**从验证失败的类型入手（语法/ 逻辑/超时），分别讲对应的修复策略。重点讲如何避免无限循环

（max_reflection_round 限制）。

### Q4："如果向量检索召回不准确怎么办？"

**策略：**从多个维度回答：chunking 策略优化（语义分块）、embedding 模型选择（中文 bge-large-zh）、混合检索

补充关键词信号、rerank 二次排序。

### Q5："这个项目最大的技术难点是什么？"

**策略：**诚实回答 SQL 生成质量本身——LLM 的幻觉问题无法彻底消除，反思机制只能覆盖常见错误。真正的难点在

于平衡召回率和精确率。

## 四、简历避坑指南

#### 错误示范 vs 正确示范

| 错误写法 | 正确写法 | 原因 |
| --- | --- | --- |
| “使用了 RAG 技术” | “基于 RAG 架构实现文档检索，通过优化 chunking 策略将检索 F1 提升 18%” | 量化结果更有说服力 |
| “负责后端开发” | “设计并实现 FastAPI REST API 服务，支持 100+ QPS” | 具体职责 + 量化指标 |
| “使用了向量数据库” | “基于 LanceDB 实现 Schema 向量检索，预计算索引将延迟从秒级降至毫秒级” | 讲清楚解决什么问题 |
| “团队协作开发” | “独立完成检索模块从设计到上线的全流程” | 突出个人贡献 |
| “熟练使用 Python” | “使用 Python 3.12 + FastAPI 实现异步 API，通过 uv 管理依赖” | 技术栈具体化 |

### 四条原则

1. 动词开头：设计、实现、优化、搭建、构建
2. 量化优先：提升X%、降低 Xms、支持N种
3. 技术具体：不写"AI技术"，写"RAG"、"向量检索"
4. 突出个人：不用"我们”，用“我设计“、"我实现"

## 五、不同岗位的简历侧重

| 岗位方向 | 简历侧重模块 | 技术关键词 |
| --- | --- | --- |
| AI 工程师 | RAG、检索优化、反思机制 | RAG、向量检索、Embedding、LLM、Prompt Engineering |
| 后端工程师 | API 服务、存储抽象、MCP | FastAPI、异步编程、向量数据库、多数据库适配 |
| 数据工程师 | NL2SQL、Schema 链接、SQL 生成 | LanceDB、向量检索、SQL 生成、多数据库方言 |
| 平台工程师 | MCP、工具生态、Skills 系统 | MCP 协议、工具注册、权限管理 |

## Data_engineer 一面试问答精编（30+）

每题含：问题、参考答案（约200~300字量级）、面试官想听的点、常见踩坑。

## 类别一：项目整体设计

### Q1.项目的整体架构是什么样的？

**参考答案：**

是一个基于工作流编排的数据工程智能体。用户通过CLI 或 API发起查询请求，请求首先进入 Agent 类，由 Workflow 管理执行流程。Workflow 由多个 Node 节点组成，节点按预设顺序执行（Begin -> Selection -> SchemaLinking -> GenSQL -> Execute -> Output）。

核心处理引擎在 datus/agent/node/ 目录，存储层在 datus/storage/。存储层使用 LanceDB 向量数据 库，抽象出 BaseEmbeddingStore 基类，其下有 DocumentStore（文档检索）、SchemaWithValueRAG （Schema 元数据）、MetricRAG（业务指标）等子类。

**面试官想听的点：**分层清晰、模块职责明确、能画出架构图、Node 工厂模式

**常见踩坑：**只讲技术栈不讲架构，或把架构说成"一个 Agent处理所有请求“——说明没有理解节点拆分的设计。

### Q2.为什么选择工作流节点编排而不是纯 Agent模式？

纯 Agent 模式（如 AutoGPT）的优点是灵活，但缺点是调试困难、成本高、延迟大。SQL 生成流程中大部分步骤是 确定性的：Schema 链接、执行验证的逻辑是固定的，不需要LLM 动态决策。 采用"结构化 Workflow +AgenticNode"的混合模式+AgenticNode"的混合模式：Workflow 固定执行顺序保证可 预测性，GenSQLAgenticNode 内部通过LLM 驱动生成和反思，保证灵活性。这兼顾了效率和能力。

**面试官想听的点：**理解 Workflow 和 Agent 的权衡、能说清楚各自适用场景、工程化思维

**常见踩坑：**说"因为纯 Agent 太慢了"——这是结果不是原因，应该从架构层面分析。

### Q3. 为什么不用 LangGraph 或 CrewAI？

LangGraph 和 CrewAI是通用 Agent 框架，不针对 SQL 生成场景定制。本项目从第一天就围绕 NL2SQL场景设计：

1. 内置 SchemaLinkingNode，不需要自己接入 Schema 检索
2. 内置 ExecuteSQLNode，实际执行 SQL 验证结果
3. 内置11 种数据库适配器，覆盖主流 BI场景
4. MetricFlow 集成，支持业务指标的语义层抽象
MCP （Model Context Protocol）是 Anthropic 提出的标准，让AI与外部工具交互有统一规范。本项目实现MCP的 价值：

**面试官想听的点：**对竞品有了解、能讲清楚差异化价值、场景驱动技术选型

**常见踩坑：**说"因为这是我们自己的项目“——这是主观原因，应该从功能差异角度分析。

### Q4. Node 节点是如何管理的？

**参考答案：**

通过工厂模式管理：Node.new_instance()根据 node_type 参数创建对应节点子类。节点类型定义在 /configuration/node_type.py，工厂映射在 /agent/node/node.py:new_instance（） 方法中。 每个 Node 有唯一ID 和 description，通过 Workflow.add_node（）加入工作流。Workflow 维护 nodes 字 典和 node_order 列表，执行时按 node_order顺序调用各节点的 execute()方法。

**面试官想听的点：**工厂模式、节点可插拔、执行顺序控制

**常见踩坑：**说"每个请求都 new 一个 Node"——实际上节点是共享复用的。

### Q5.新增一个节点需要改几个文件？

需要改3个文件：

1. /agent/node/my_node.py 一创建节点类，继承 Node，实现 execute()方法
2. /configuration/node_type.py -添加 MY_NODE = "my_node" 类型常量
3. /agent/node/node.py:new_instance（）-添加 my_node.py 的import 和 case 分支
这样新增节点完全不影响现有节点和其他模块，符合开闭原则。

**面试官想听的点：**开闭原则、工厂模式、新人能否快速上手

**常见踩坑：**说"需要改Workflow 类"——这违反了开闭原则，说明设计有问题。

### Q6.为什么需要MCP 协议？

1. 生态集成：Claude Desktop、Cursor 等 IDE 原生支持MCP，一行配置就能接入本项目的工具能力
2. 双向通信：本项目既是 MCP Server（暴露工具），也是 MCP Client（消费外部工具）
3. 标准化：不用自己实现工具注册、发现、调用协议，降低开发成本
实际使用中，用户在 Claude Desktop 配置 mcpServers 后，可直接通过自然语言调用本项目的SQL 生成、文档 检索等工具。

**面试官想听的点：**MCP 协议理解、生态意识、双向集成

**常见踩坑：**说"MCP 就是让AI调用工具"——太浅，应该从协议层和生态角度讲。

## 类别二：核心难点一并行与性能

### Q7. 向量检索的性能瓶颈在哪里？

**参考答案：**

向量检索的性能瓶颈主要在三个环节：

1. Embedding生成：单次请求20-50ms，主要消耗在GPU 推理。本项目使用
get_document_embedding_model （） 获取模型，batch_size 默认 32。

2. ANN 检索：LanceDB 默认 IVF_FLAT,1000行以内数据直接暴力搜索；超过5000行自动切换 IVF_PQ。本项目
的优化在 create_vector_index()方法中根据数据量选择索引类型。

3. 结果解析：返回大量行时网络传输和序列化耗时。
的并行处理 优化思路：预计算+批量查询+索引分区。本项目的 Schema 预加载和 StreamingDocProcessor 都是这类优化。

**面试官想听的点：**能定位具体瓶颈点、懂 ANN 算法选择依据、知道优化方向

**常见踩坑：**说"向量检索很快不需要优化"——说明没有遇到过性能问题。

### Q8. 如何优化 LLM 的 Token 消耗？

Token 消耗主要在 Prompt构建和生成输出两个环节。本项目的优化策略：

1. Prompt 压缩：GenSQLAgenticNode 只注入相关的 Schema（按 target_tables 过滤），而不是全量 Schema
2. Few-shot 精简：参考 SQL 只取top_k=3 个最相关的，不是无限注入
3. 结果缓存：相同 query 的生成结果可以缓存，避免重复LLM 调用
4. 模型路由：简单查询用小模型（GPT-4.1-mini），复杂查询用大模型（GPT-4o）
实际成本：一次 SQL 生成平均消耗 500-800 Token input + 200-400 Token output，相比直接用GPT-4o生成完整 ETL 管道代码节省 60%+。

**面试官想听的点：**成本意识、缓存策略、模型分级

**常见踩坑：**说"没有考虑过 Token 成本"——说明没有生产环境经验。

### Q9.并行执行的状态冲突如何解决？

本项目在 StreamingDocProcessor 中使用 ThreadPoolExecutor 并行处理多个文档，状态冲突通过两种方式解 决：

1. 不可变结果：每个线程返回独立的 FetchedDocument 对象，不修改共享状态
2. 线程安全统计：ProcessingStats 用 threading.Lock 保护计数器
```python
stats.increment(docs=1, chunks=len(chunks))  # 线程安全
```

如果涉及写操作（如结果合并），使用with self._lock：保护临界区。Python 的GIL 在I/O密集型场景下不影 响性能。

**面试官想听的点：**线程安全实现、锁粒度选择、GIL理解

**常见踩坑：**说"用全局变量共享状态"——这会导致竞态条件。

### Q10.缓存一致性问题如何处理？

**参考答案：**

本项目使用 delete-then-add 而非 merge_insert 处理缓存一致性。原因：merge_insert 在并发写入时可能出现 commit conflict，而 delete-then-add 先删后加是原子操作。

```python
# 删除已有 chunk
self.table.delete(in_("chunk_id", batch_ids))
```

```python
# 写入新 chunk
self.store_batch(data)
```

对于 Schema 元数据缓存，由于是预计算数据（不会在运行时修改），直接用 Lru_cache 缓存实例，不存在一致 性问题。

**面试官想听的点：**事务理解、并发意识、缓存策略选择

**常见踩坑：**说"直接覆盖写入"——这可能导致数据丢失或不一致。

## 类别三：核心难点—循环与流程控制

### Q11.反思机制是如何设计的？

反思机制是多轮验证-修复循环：

1. 验证阶段（GenSQLAgenticNode._verify_sql）：语法检查用 SQLGlot，逻辑检查用LLM 反思
2. 错误分析（ReflectNode）：分类错误类型——语法错误（缺少括号）、列名错误（表里没这列）、逻辑错误
（WHERE 条件不合理）

3. 修复阶段（FixNode）：针对错误类型调用LLM 生成修复后的 SQL
4. 终止条件：reflection round >= 3 或人工触发 HITL
4. 终止条件：
reflection_round >= 3 或人工触发 HITL

```python
if not is_valid:
    state.reflection_needed = True
    state.error = error
    state.reflection_round += 1
```

**面试官想听的点：**状态机思维、错误分类、终止条件设计

**常见踩坑：**说"反思就是让 LLM 重新生成一次"——没有理解验证-分析-修复的闭环。

### Q12. 如何防止无限循环？

**参考答案：**

本项目通过三重保护防止无限循环：

1. 最大反射次数：reflection_round >= 3 强制终止
ExecuteSQLNode 设置30s 执行超时

2. 超时机制：
3. 人工兜底：
HITLNode 作为最后一道防线，将问题转给人工

```python
if state.reflection_round >= 3:
    state.status = "max_reflection_reached"
    return state
```

```python
if execution_timeout:
    state.error = "timeout"
    return state
```

**面试官想听的点：**防御性编程、多层保护、设计优先级

**常见踩坑：**说"理论上不会无限循环"——应该讲清楚实际的保护机制。

### Q13.如果所有反思都失败了怎么办？

触发 HITL （Human-In-The-Loop）机制：系统不再尝试自动修复，而是将问题、降级后的SQL选项、错误日志打包，通过 HITLNode 暂停工作流，等待人工决策。 用户可以通过 CLI 查看失败详情，选择：1）接受部分正确的SQL 手动修改；2）提供更详细的上下文；3）放弃本次 查询。

这个设计符合工程实践——不是所有问题都要自动解决，明确系统边界更重要。

**面试官想听的点：**工程边界意识、用户体验设计、容错降级

**常见踩坑：**说"会一直重试直到成功"——这会导致无限循环，是严重的设计缺陷。

## 类别四：工程化

### Q14.如何保证代码质量？

**参考答案：**

本项目通过多层次保证代码质量：

1. 静态检查：Ruff （format + lint）在 pre-commit 时运行，E/W/F/B/I/C90 规则覆盖
2. 类型检查：使用完整 type hint + mypy 检查
3. 单元测试：
tests/unit_tests/ 目录下每个模块有对应测试，CI级别测试覆盖率要求80%+

4. diff coverage：不仅看整体覆盖率，还要求新增代码 80%+有对应测试
5. 代码审查：PR 必须经过 review,Commit Message 有格式要求（［Feature］/［BugFix］/［Refactor］ 等前缀）
```bash
uv run pytest tests/unit_tests/ --cov=datus --cov-fail-under=80
uv run diff-cover coverage.xml --compare-branch=upstream/main --fail-under=80
```

**面试官想听的点：**测试覆盖率意识、自动化流程、代码规范

**常见踩坑：**说"我们主要靠人工 review"——没有自动化测试的项目不可维护。

### Q15.Schema 演进如何处理？

Schema 演进（表结构变更）通过CDC模式处理：

1. 初始化：init_local_schema（）扫描数据库表结构，生成 embedding 存入 LanceDB
2. 变更检测：通过文件 hash 对比判断 Schema 是否变化
3. 增量更新：变化时删除| Schema，重新计算 embedding
```python
# 增量更新逻辑
if compute_hash(new_schema) != stored_hash:
    delete_old_schema(doc_path)
    store_new_schema(new_schema)
```

**面试官想听的点：**版本管理意识、增量更新思维

**常见踩坑：**说"每次都全量重新加载“——这在大表场景下不可接受。

### Q16.日志和可观测性如何设计？

**参考答案：**

本项目使用统一的日志规范：

1. 日志框架：通过 get_logger （name）获取logger，格式化统一
2. 日志级别：INFO（正常流程）、WARNING（非致命问题）、ERROR（需要关注的问题）
3. 结构化日志：包含task_id、node_id 等上下文字段，方便排查
```python
logger = get_logger(__name__)
logger.info(f"Processed {stats.total_docs} docs, {stats.total_chunks} chunks")
```

追踪方面，使用 optional_traceable 装饰器支持链路追踪注入。关键指标：检索延迟、SQL 生成成功率、执 ProcessingStats 统计。 行时间等通过

**面试官想听的点：**日志规范意识、上下文埋点、关键指标

**常见踩坑：**说"用 print 调试"——生产环境不能用 print。

### Q17.密钥管理如何处理？

本项目的密钥管理原则：

1. 不硬编码：API Key 存储在环境变量或 agent.yml，使用$｛ENV_VAR｝语法引用
2. YAML 隔离：敏感配置在 agent.yml 中，YAML 文件不提交到代码仓库
3. 运行时替换：
$｛OPENAI_API_KEY｝ 在运行时被环境变量值替换

```yaml
# agent.yml 配置示例
provider:
  api_key: ${OPENAI_API_KEY}
```

**面试官想听的点：**安全意识、环境隔离、配置分离

**常见踩坑：**说"先把 Key 写死在代码里，后面再改"——这是安全大忌。

## 类别五：模型/算法相关

### Q18.Embedding 模型如何选择？

**参考答案：**

Embedding 模型选择取决于场景：

| 模型 | 维度 | 适用场景 | 成本 |
| --- | ---: | --- | --- |
| text-embedding-3-small | 1536 | 通用场景，性价比高 | 低 |
| text-embedding-3-large | 3072 | 高精度需求 | 中 |
| bge-large-zh | 1024 | 中文场景，开源免费 | 0 |

本项目默认使用384维 embedding （get_document_embedding_model 返回模型 dim_size=384），兼顾检 索质量和存储开销。对于中文文档，考虑切换到 bge-large-zh。

**面试官想听的点：**模型选型依据、中英文差异、成本意识

**常见踩坑：**说"用最大的模型"——没有免费的午餐，要考虑成本。

### Q19.如何解决 RAG的幻觉问题？

RAG 幻觉指检索结果不相关或生成答案与检索内容不符。本项目的解决思路：

1. 检索层：混合检索（向量+BM25）+多字段加权+多样性约束，提升召回质量
2. 生成层：Prompt约束"只基于检索结果生成，不要自行编造"
3. 验证层：SQL 生成后通过执行验证结果合理性（空结果、异常值检测）
```python
if result.is_empty:
    sql_state.warning = "Query returned no results"
elif result.has_nulls:
    sql_state.warning = "Result contains null values"
```

**面试官想听的点：**幻觉来源理解、多层防护、验证兜底

**常见踩坑：**说"RAG 不会有幻觉"——这是错误的，幻觉来源是检索和生成两端。

### Q20.Rerank 是怎么做的？

**参考答案：**

本项目的 Rerank 是轻量级的多字段加权，而非 Cross-Encoder 二次排序： Python

```python
final_score = (
    0.5 * vector_score      # 向量相似度
    + 0.3 * text_score      # BM25 得分
    + 0.1 * title_boost     # 标题命中
    + 0.05 * hierarchy_boost # 层级命中
    + 0.05 * keywords_boost  # 关键词命中
)
```

```python
final_score = (
    0.5 * vector_score
    + 0.3 * text_score
    + 0.1 * title_boost
    + 0.05 * hierarchy_boost
    + 0.05 * keywords_boost
)
```

轻量级 Rerank的优势：不需要额外调用LLM 或模型，延迟低；缺点：不如 Cross-Encoder 精确。如果需要更高精 度，可引入 datus-storage-base 的 cross-encoder 功能。

**面试官想听的点：**Rerank 原理、权重设计、轻量级 vs 重型方案

**常见踩坑：**说"Rerank 就是把结果再排一遍“——没有讲清楚加权公式和设计依据。

### Q21.Chunking策略是怎样的？

**参考答案：**

文档分块（Chunking）在 SemanticChunker 中实现，基于文档结构（标题层级、段落）的语义分块，而非固定 大小切分：

1. 层级拆分：max_heading_depth=3 限制，h4 以下内容扁平化到父节点
2. 段落优先：尽量保持完整段落，避免跨段落切分
3. 重叠保留：
chunk_overlap=128 在块边界保留重叠内容，避免信息丢失

4. 小型合并：小于 min_chunk_size=256 的块会合并到相邻块
```python
# 语义分块时保留标题层级与段落结构
flat_text = self._flatten_section_content(section)
return self._split_content(flat_text, ...)
```

**面试官想听的点：**chunking策略选择、语义完整性和召回率的平衡

**常见踩坑：**说"用固定大小切分就行"——这会破坏语义完整性。

### Q22.评估指标有哪些？

本项目的评估指标体系：

1. 检索质量：F1（Precision + Recall）、NDCG
2. 生成质量：SQL 语法正确率、执行成功率
3. 性能指标：检索延迟、端到端响应时间
4. Benchmark: BIRD dataset、Spider 2.0-Snow
```python
precision = relevant_retrieved / retrieved
recall = relevant_retrieved / relevant
f1 = 2 * precision * recall / (precision + recall)
```

Benchmark 结果在 benchmark 目录下，展示了不同配置下的准确率对比。

**面试官想听的点：**评估体系完整、指标可量化、Benchmark 意识

**常见踩坑：**说"我们靠用户反馈"——没有系统化的评估体系。

## 类别六：综合题

### Q23.如果让你重新设计这个项目，你会怎么改？

**参考答案：**

如果重新设计，我会考虑：

1. 存储层分离：当前 Schema 元数据和 DocumentStore 耦合过紧，应该统一抽象为 RetrievalStore 接口，支
持切换不同的向量后端（Milvus、Pinecone）

2. 反思机制独立：当前反思和生成在同一节点，可以拆分为独立的 ReflectAgent，支持配置不同的反思策略
3. 评估内置：benchmark 和评估框架应该在CI中自动运行，而不是手动触发
4. 流式输出：当前结果是整体返回，可以改造为流式输出，用户体验会更好
**面试官想听的点：**主动思考、发现问题、有改进思路

**常见踩坑：**说"不需要改"——说明没有深入思考项目局限。

### Q24.这个项目如何部署到生产环境？

生产环境推荐 Docker Compose 部署： datus-api REST API 服务，水平扩展

1. 核心服务：
2. MCP 服务：datus-mcp MCP Server，独立进程
3. 向量库：LanceDB 嵌入式，无需单独部署
4. 会话存储：
~/.datus/sessions/映射到持久化存储

```bash
docker-compose up \
  -e DATA_ENGINEER_API_IMAGE=datus/datus-agent:latest \
  -v ~/.datus/sessions:/root/.datus/sessions
```

监控方面，可接入 Prometheus + Grafana，关键指标：API QPS、检索延迟、SQL 生成成功率。

**面试官想听的点：**生产部署意识、Docker 使用、监控方案

**常见踩坑：**说"直接跑在服务器上"——没有容器化意识。

### Q25.项目最大的技术难点是什么？

最大的难点是SQL 生成质量的稳定性。表面上是技术问题（检索、反思），实际上核心是：

1. 语义理解的边界：用户表达模糊时（如"按月统计"可能指日历月或财月），LLM 可能理解错误
2. Schema 覆盖的不完整性：表结构信息可能不包含业务含义（如某列存的是 status_code 但描述是"状态"）
3. 反思的有限性：反思只能修复常见错误，复杂逻辑错误无法自动发现
我的应对策略：1）通过 few-shot learning 提供更多参考 SQL；2） Schema 描述尽量完整；3）预留 HITL 作为兜底。不追求100%自动解决，追求 80%场景下用户零人工介入。

**面试官想听的点：**诚实面对局限、解决问题思路、期望管理

**常见踩坑：**说"没有难点"——这是不现实的。

## Data_engineer - 技术面总结

### 项目基础问题

### 介绍一下这个项目？

Data_engineer 是一个数据工程智能体，通过自然语言处理和语义搜索，将自然语言查询转换为准确的SQL。核心是 基于工作流节点编排的系统，把SQL 生成分解为意图分类、Schema 链接、上下文检索、LLM 生成、执行验证等阶 段，每个阶段由专门节点处理，通过有向无环图实现灵活编排。

### 这个项目是否涉及到harness？

是的，这个项目深度体现了 agent 设计的 harness 技术架构。 data-engineer 的核心设计不是让 LLM 作为一个黑盒自由决策，而是将LLM“装进"一套严格的结构化框架（即 harness/外骨骼）中进行可控执行。这套 harness 体现在以下层面：

1. Workflow + Node 双层抽象：Node 抽象基类定义了统一的执行接口（execute / setup_input /
update_context），每种 LLM 调用（Schema Linking、SQL 生成、执行、反思等）被封装为特定类型的节点，通 过 workflow.yml 声明的 Plan 模板（如reflection、chat_agentic、gensql_agentic 等）编排成 DAG 拓扑序执行， 而非让 LLM 自行决定下一步做什么。

2. AgenticNode 作为强化 harness：继承自 Node 的 AgenticNode 为每个节点注入了 session 管理
（AdvancedSQLiteSession）、tool集成 （func tools + MCP servers）、权限管控（PermissionManager 三级 allow/deny/ask）、技能系统（SkillManager +SkillFuncTool）、Action 历史追踪（ActionHistoryManager）、自 动上下文压缩（auto-compaction at 90% token usage）以及streaming执行支持，这些全部内嵌在 harness 层

面，节点实现者无需关心。

3. WorkflowRunner 作为harness 的执行引擎：WorkflowRunner 负责工作流的生命周期管理（初始化、节点推进、
evaluate_result质量评估、失败处理、轨迹持久化），按 node_order 顺序推进而非让 LLM 自由跳转，确保执行 路径可预测、可审计、可复现。

4. 配置驱动的声明式 harness：通过 agent.yml 声明式配置 provider、节点模型、工具权限、技能模式等，Agent的
运行时行为完全由外部 YAML 配置决定，LLM 本身不具备突破 harness 约束的能力。

简而言之，这个项目的 harness 范式就是：LLM 被"拴"在一套由 Node Workflow WorkflowRunner Agent四 级结构组成的受控管道中，每一步执行都受到输入/输出类型约束、权限校验、质量评估和状态追踪的严格治理，而 非让 LLM 作为自主 Agent 自由决策。

### 这个项目和同类项目有什么区别？

| 维度 | Data_engineer | LangChain | AutoGPT |
| --- | --- | --- | --- |
| 核心场景 | NL -> SQL | 通用 Agent | 通用自动化 |
| Schema 理解 | 内置向量检索 | 需自行集成 | 无 |
| SQL 验证 | 多阶段验证反思 | LLM 自检 | 无 |
| 数据库支持 | 11 种内置 | 需适配器 | 无 |
| 语义层 | MetricFlow 集成 | 无 | 无 |

在 Data_engineer 中，语义分块器（SemanticChunker）基于文档结构（标题层级、段落）做智能分块，保留完整的 语义单元，同时通过 overlap 避免边界信息丢失。

## 核心技术问题

## RAG 相关

### Q：什么是 RAG？为什么它比直接让模型回答更适合企业知识问答？

RAG（检索增强生成）通过从企业知识库检索相关文档作为上下文，让 LLM 基于真实数据生成答案。相比直接让 LLM 回答，RAG 的优势在于：答案基于实际检索到的内容而非模型记忆，因此不会产生幻觉；企业知识随时更新， RAG 能及时反映最新信息；每个答案可附带引用来源，方便用户核实。

### Q：RAG 和微调有什么区别？什么时候用哪个？

RAG改变的是推理时输入的上下文，不改变模型本身；微调是通过训练改变模型的权重。RAG 适合知识会频繁更新、需要引用来源、多个知识领域共存的场景；微调适合需要模型学习特定格式、语气或领域专有推理方式的场景。

### Q：为什么说 chunking 决定了检索系统的上限？

Chunk 太小会丢失上下文导致答案碎片化，chunk 太大引入过多无关内容增加噪音。在 Data_engineer 中，语义分块器（SemanticChunker）基于文档结构（标题层级、段落）做智能分块，保留完整的语义单元，同时通过 overlap 避 免边界信息丢失。

### Q：Embedding 模型怎么选？

中文场景用 bge-large-zh（开源免费，中文效果最佳）；通用场景用text-embedding-3-small 性价比最高；高精度需求用 text-embedding-3-large。

### Q：为什么很多系统要加 rerank？

向量检索基于近似最近邻（ANN），追求速度但精度有限。Cross-Encoder 用完整 Transformer 对 query 和 doc 做 精确相关性评分作为二次排序，能显著提升检索质量。Data_engineer 中通过多字段加权（title、hierarchy、 keywords）和多样性约束实现轻量级 rerank。

### Q：Hybrid Retrieval 的本质是什么？

同时使用多种检索方法（向量检索+关键词检索），各自取 Top-K 结果后加权融合。向量检索擅长语义理解，关键词检索擅长精确匹配，Data_engineer 的 OptimizedRecall 类实现了 BM25+向量的混合检索，通过可配置的权重组合两种信号。

## Agent 相关

### Q：什么是 Agent？跟传统的Chain 有什么区别？

Agent 是具有自主决策能力的 AI程序，包含LLM 核心、规划能力、记忆和工具使用四个组件。Chain 执行预定义的 固定流程，Agent 根据中间结果动态决定下一步，更灵活但也更难调试。Data_engineer 使用工作流节点图来约束执行路径。

### Q：多 Agent 系统的编排模式有哪些？各自优缺点？

| 模式 | 特点 | 适用场景 |
| --- | --- | --- |
| Boss-Worker | 中央协调者分配任务 | 有明确协调者 |
| Pipeline | 线性流程，上游输出是下游输入 | 步骤明确、依赖清晰 |
| 讨论模式 | 多 Agent 平等协作 | 需要多视角分析 |

Data_engineer 采用 Pipeline + 条件分支的混合模式，通过 Workflow 管理节点执行顺序，SelectionNode 做意图分类实现条件路由。

### Q：如何解决多 Agent 间的循环依赖和无限循环？

GenSQLAgenticNode 的反思机制设置最大迭代次数（reflection_round 限制）、超时控制、Token 预算限制。 最多重试 3 次，超过后触发人工介入（HITLNode）。

### Q：你的 Agent 系统如何保证容错性？

1. 各节点独立执行，单节点失败不影响其他节点
2. SQL 执行有超时保护（30s）和异常捕获
3. 反思机制自动修复常见错误
4. 降级策略：验证失败时提供备选方案

## GraphRAG 相关

### Q：知识图谱在 RAG 中起什么作用？

纯向量检索只能捕获语义相似性，无法理解实体间的结构化关系。知识图谱保留实体间的显式关系（who -> works_at -> where），支持多跳推理：本项目的 Schema 元数据存储了表间关系，支持跨表 JOIN 路径推理。

### Q：子图检索的 Cypher 查询怎么写？

```cypher
MATCH path = (start:Table {name: $table})-[*1..2]-(neighbor)
RETURN start.name, type(relationship), neighbor.name
LIMIT 50
```

可变长度路径匹配 [*1..2] 实现多跳遍历，本项目的 Schema Linking 通过类似思路发现间接相关的表。

## 框架对比相关

### Q：LangGraph vs CrewAI vs AutoGen 怎么选？

| 维度 | LangGraph | CrewAI | Data_engineer |
| --- | --- | --- | --- |
| 控制粒度 | 有向图 | 角色定义 | 节点图 |
| 上手难度 | 中等 | 简单 | 中等 |
| SQL 场景 | 需自行开发 | 无 | 内置 |
| 数据库支持 | 无 | 无 | 11 种 |

本项目专注于数据工程场景，内置 SQL 生成、Schema 链接、执行验证，无需从头开发。

### Q：为什么选这个框架而不是直接调用？

1. 内置工作流编排，不需要手动管理状态传递
2. 节点可复用，不同查询可共用 Schema 链接、反思等节点
3. 支持 Plan 模式，复杂查询可先预览再执行
4. 内置 MCP 协议支持，开箱即用的 IDE 集成

## 系统设计相关

### Q：系统的性能瓶颈在哪里？怎么优化？

| 当前方案 | 瓶颈 | 优化方向 |
| --- | --- | --- |
| 向量检索 | Schema 检索 | 预计算索引 |
| LLM 生成 | API 调用 | 响应缓存 |
| SQL 验证 | 语法解析 | 流式验证 |

向量索引已通过 create_vector_index() 创建 IVF_PQ 索引；LLM 生成可通过结果缓存复用相同查询的 SQL。

### Q：如果文档规模扩大到 100 万，系统怎么扩展？

1. 向量库：从 LanceDB 单机迁移到 Milvus 集群（支持百亿级向量）
2. 文档解析：多 Worker 并行处理，Celery 任务队列
3. API 层：水平扩展，Kubernetes 多副本
4. 缓存：引入 Redis 缓存热点查询结果
## 综合开放问题

### 被质疑只是复现跑了一下项目，怎么回答？

这个项目我参与了核心检索模块的设计和实现。具体来说：1）我设计了混合检索策略，将BM25 与向量检索结合， 通过可配置的权重机制实现准确率提升；2）我实现了语义分块器，基于文档结构做智能分块，而不是简单的固定大 小切分；3）我优化了 Schema 链接流程，通过预计算索引将检索延迟从秒级降到毫秒级。这些改进都在 benchmark 上有量化指标支撑。

### 这个项目有部署上线吗？

是的，项目已在公司内部部署使用。主要部署模式：1）CLI模式供数据工程师日常使用；2）API 模式集成到内部数 据平台；3）MCP 模式提供给 Claude Desktop 用户使用。生产环境使用 Docker Compose 部署，包含 API服务、 MCP 服务和 LanceDB 向量库。

### 测完接口性能后，你思考过如何优化吗？

有几个优化方向：1）结果缓存，对相同查询直接返回缓存的 SQL；2）批量预热，闲时预加载热点 Schema 到内存；3）模型蒸馏，用大模型生成的 SQL 作为伪标签，训练小模型做快速生成；4）索引优化，根据查询分布动态调整IVF 索引的分区数。

## Data_engineer 一技术面试「八股文」知识库

面向 AI/数据工程师岗位的系统化复习材料。可与本仓库 datus/目录实现对照阅读。每个主题含：概念辨析、适 用场景、与本项目联系、简短代码或伪代码、常见面试追问。

1. Agent vs Workflow vs Multi-Agent
Agent：具有自主决策能力的AI 程序，核心组件包含LLM 思维引擎、规划能力、记忆系统、工具调用。Agent 根据 中间结果动态决定下一步，而非按预设流程执行。 Workflow：预先定义好执行顺序的节点图（Pipeline/ DAG），节点间有明确的依赖关系，执行顺序固定。本项目的 workflow 即此模式。 Multi-Agent： 多个专业 Agent 协作，各 Agent 职责单一，通过消息传递或共享状态协作。本项目采用单主 Agent +

多专业节点的模式 三者对比：Agent适合开放性任务（需要动态决策），Workflow 适合确定性任务（路径已知），Multi-Agent适合复 杂任务的职责拆分。

本项目：Agent 类负责任务编排，Workflow 管理节点执行顺序，Node 是执行单元。 GenSQLAgenticNode 内部包含LLM 驱动的反思决策，是 Agent 模式的体现。

```python
# 本项目 Workflow 的执行模式（伪代码）
class Workflow:
    def run(self):
        for node_id in self.node_order:
            node = self.nodes[node_id]
            state = node.execute(state)  # 固定顺序执行
```

**面试追问：**「为什么不用纯 Agent 模式？」——因为 SQL 生成流程的大部分步骤是确定的（Schema 链接、执行验

证），用Workflow 可以减少LLM 调用次数，降低成本和延迟。

2. Pipeline / DAG / 状态机
Pipeline：线性流水线，上游输出直接流入下游，适合各阶段输出独立的场景。 DAG（有向无环图）：允许并行分支和条件路由，但不允许环。本项目的 Workflow 即 DAG——节点间有依赖但不 构成环。 状态机：通过状态转移规则驱动，状态变更触发下一步行动。适合状态驱动的工作流。

本项目：Workflow 实现 DAG，通过 node_order 确定拓扑序。SelectionNode 的意图分类结果决定后续 分支，实现条件路由。

```python
# DAG 拓扑排序（伪代码）
# 本项目的 Workflow 按 add_node 顺序决定 node_order
workflow.add_node(BeginNode(), position=0)
workflow.add_node(SchemaLinkingNode(), position=1)
workflow.add_node(GenSQLAgenticNode(), position=2)
# node_order = [BeginNode, SchemaLinkingNode, GenSQLAgenticNode]
```

3. ReAct / CoT / Reflection
ReAct （Reasoning + Acting）：交替进行推理和动作执行，边想边做，适合需要外部工具调用的场景。 CoT（Chain of Thought）：让模型逐步推理，输出推理链，适用于数学和逻辑问题。 Reflection：对生成结果进行自我反思，发现错误并修正。本项目的 ReflectNode + FixNode 即此模式。

本项目：GenSQLAgenticNode 先用 CoT 方式理解查询意图，再用 Reflection 验证生成的 SQL是否正确、逻辑是 否合理。

```python
# 反思机制（伪代码）
if not self._verify_sql(generated_sql):
    state.reflection_needed = True
    error = self._analyze_error(generated_sql)
    # FixNode 修复后重新验证
```

4. Tool Calling/Function Calling
Tool Calling：让 LLM 生成结构化的工具调用指令（如JSON），而非自然语言。Function Calling 是 OpenAI 的实现版本。

本项目：通过 FuncTool 抽象将 Python 函数暴露给 LLM。 trans_to_function_tool 装饰器将函数签名转换 为LLM 可调用的工具定义。

```python
class FuncToolResult:
    success: int  # 1=成功，0=失败
    result: Any   # 返回数据
    error: str    # 错误信息
```

```python
# 工具返回统一结构，供 LLM 判断调用是否成功
FuncToolResult(success=1, result=data, error="")
```

统一的工具返回结构可以帮助 LLM 判断工具调用是否成功，并避免调用不存在的工具。

5. MCP （Model Context Protocol）
MCP：Anthropic 提出的标准协议，让 AI Agent 标准化地调用外部工具和服务。MCP Server 暴露工具，MCP Client 消费。

本项目：既实现了 MCP Server（通过 datus-mcp 暴露工具给 Claude Desktop、Cursor 等 IDE），也是 MCP Client（通过 MCP 配置消费外部工具）。
```python
class MCPServer:
    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool

    def handle_request(self, request):
        tool = self.tools[request.tool_name]
        return tool.execute(request.params)
```

6. 向量数据库与 Embedding
向量数据库：存储高维向量（embedding），通过ANN（近似最近邻）算法实现语义相似度检索。代表产品： LanceDB、Milvus、Pinecone。 Embedding：将文本/图片等转换为高维向量的模型。维度越高信息越丰富，但检索成本越高。

本项目：使用 LanceDB 存储向量，通过 get_document_embedding_model 获取 embedding 模型，维度默认 384。DocumentStore 的 search_docs 方法执行向量检索。

```python
# 向量检索（伪代码）
query_vector = embedding_model.embed(query)
results = table.search_vector(
    query_vector,
    top_k=top_n,
    where=version_filter,
)
```

7. RAG 与 Agent 的结合
RAG （Retrieval Augmented Generation）：在 LLM 生成答案前，先检索相关文档作为上下文，解决LLM 知识过时 和幻觉问题。 RAG + Agent: Agent 在执行过程中调用 RAG 检索外部知识，检索结果作为 Prompt 上下文。本项目即此模式—— GenSQLAgenticNode 在生成 SQL 前先通过 DocumentStore 检索相关文档和参考 SQL。

```python
# RAG 检索作为上下文（伪代码）
docs = doc_store.search_docs(query=nl_query, top_k=5)
ref_sqls = ref_sql_store.search_reference_sql(query=nl_query, top_k=3)
```

```python
prompt = (
    f"参考文档：{docs}\n"
    f"参考 SQL：{ref_sqls}\n"
    f"问题：{nl_query}"
)
```

优化方向包括 chunking strategy（语义分块）、embedding 模型选择（中文 bge）、rerank（多字段加权）、query expansion（扩展同义词）。

8. 并行执行与状态合并
并行执行：多个任务同时执行，提高吞吐量。本项目 StreamingDocProcessor 使用 ThreadPoolExecutor 并行处理多个文档。 状态合并：并行分支执行完毕后，需要合并各分支的结果。本项目在 SchemaLinkingNode 中并发检索多个表的 Schema，合并到 target_tables。

```python
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(search_table, t) for t in tables]
    results = [f.result() for f in futures]
merged = {r.table_name: r for r in results}
```

对象而非修改）。

9. 循环的终止条件设计
终止条件：防止 Agent/Workflow 进入无限循环，需要明确的退出条件。

本项目：Workflow 设置 reflection_round 限制反思次数，execute_sql_node.py 设置30秒执行超时。

```python
# 终止条件（伪代码）
if state.reflection_round >= 3:
    state.status = "max_reflection_reached"
    return state

if execution_timeout:
    state.error = "timeout"
    return state
```

### 10. 熔断与降级策略

熔断：当外部服务失败率超过阈值时，快速失败（熔断）避免资源耗尽，而不是重试到超时。 降级：当服务不可用时，返回降级结果（如静态数据、缓存结果）而不是直接报错。

本项目：MCP 工具注册使用降级策略——当工具不可用时（has_xxx_tools = False），工具列表中就不出现 该工具，而不是抛出错误。

```python
# 降级策略示例
if self.has_metrics:
    tools.append(trans_to_function_tool(self.search_metrics))
# 不抛异常，只是跳过不可用的工具
```

### 11.缓存策略

缓存：避免重复计算和重复 API调用，提升响应速度、降低成本。

本项目：使用多级缓存——Embedding模型使用 lru_cache 缓存结果 （get_document_embedding_model），DocumentStore 使用 lru_cache 缓存实例 （document_store.cache_clear（））。

```python
@lru_cache(maxsize=8)
def document_store(platform: str) -> DocumentStore:
    """每个平台返回独立缓存的实例。"""
    return DocumentStore(...)
```

**面试追问：**「缓存一致性问题如何处理？」——本项目使用删除后重新写入（delete-then-add）而非

merge_insert，避免写入冲突。

### 12. 知识增强—BM25与向量检索混合

BM25：基于词频的经典检索算法（类似 TF-IDF），精确匹配关键词时效果优于向量检索。 向量检索：基于语义相似度，适合同义词和语义扩展。 混合检索：同时使用两种方法，按权重融合结果。本项目的 OptimizedRecall 类实现此策略

```python
# 混合检索（伪代码）
bm25_score = bm25.score(query, doc_index)
vector_score = 1.0 / (rank + 1)  # 从排名推导
final_score = 0.5 * vector_score + 0.3 * bm25_score + 0.2 * field_boost
```

**面试追问：**「混合检索的权重如何确定？」——可以通过 grid search在测试集上寻优，或根据线上用户点击数据动

态调整。

### 13. SQL执行验证与反思

SQL 验证：语法检查（SQLGlot）、执行验证（实际执行）、逻辑验证（结果合理性）。 反思：验证失败后，分析错误原因并尝试修复。本项目的 ReflectNode 分析错误，FixNode 尝试修复。

```python
# 反思 + 修复流程（伪代码）
is_valid = self._verify_syntax(sql)
if not is_valid:
    error = self._analyze_error(sql)
    new_sql = self._fix_sql(sql, error)
    if self._verify_syntax(new_sql):
        state.generated_sql = new_sql
```

**面试追问：**「如果反思 3 次都失败了怎么办？」——触发 HITLNode（Human-In-The-Loop），将问题转给人工处理。

### 14. 可观测性一日志与 Trace

日志：结构化日志记录关键事件（INFO/WARNING/ERROR），方便排查问题。 Trace：请求级别的调用链追踪，串联一个请求在多个模块间的执行路径。

本项目：使用统一的 get_logger(name)记录日志，optional_traceable 装饰器支持链路追踪。

```python
logger = get_logger(__name__)
logger.info(f"Processed {stats.total_docs} docs, {stats.total_chunks} chunks")
logger.warning(f"Error processing {url}: {e}")
```

**面试追问：**「日志级别如何选择？」——DEBUG（开发调试）、INFO（正常流程关键节点）、WARNING（非致命问题）、ERROR（需要关注的问题）。

### 15.Schema 链接与元数据检索

Schema 链接：将自然语言查询中的实体映射到数据库表结构（表名、列名、关系）。

本项目： SchemaLinkingNode 通过 SchemaWithValueRAG 检索相关表结构，使用向量相似度匹配查询与表/列描述。

```python
# Schema 检索（伪代码）
schema_results = schema_store.search_schema(
    query=nl_query,
    datasource=datasource,
    top_k=20,
)
```

**面试追问：**「Schema 链接错了怎么办？」—— ReflectNode 会验证生成的 SQL 中引用的表和列是否在

target_tables 中，如果发现错误会触发反思修复。

## Data Engineer Agent Memory 设计详解

### 概述

Data Engineer Agent 的 memory 设计不是传统的“短期记忆/长期记忆”二分法，而是一套多层累积式上下文管理系 统，贯穿 SDK 层 -> Workflow 层 -> 反思层。整体架构如下：

```text
Prompt 层：system prompt + memory_context + AGENTS.md
SDK 层：AdvancedSQLiteSession（持久化）/ compact
Workflow 层：Context / sql_contexts / schemas / metrics / docs
反思层：StrategyType / ReflectNode 动态调整
存储层：LanceDB + SQLite / sessions / schema / metrics / docs
```

```text
Prompt 层 -> 当前 LLM 调用需要知道什么
SDK 层 -> 对话历史存在哪里、怎么压缩
Workflow 层 -> 多步任务中间结果怎么传递
反思层 -> 出错后如何调整策略和 workflow 结构
存储层 -> 跨会话知识如何持久化检索
```

**设计思路：**两条轴，四层记忆

Data Engineer Agent 的 memory 不是传统 LLM 应用里一个集中的 Memory 模块，而是沿两条轴分散到四个层次的 上下文管理体系。

**时间轴：**

```text
请求级（单次 LLM 调用） -> system prompt 中的 memory_context 注入
任务级（一次 SQL 生成） -> workflow Context 累积 sql_contexts 链
会话级（多轮对话） -> AdvancedSQLiteSession 持久化 + 自动 compact
项目级（跨会话） -> LanceDB 知识库（schema / metrics / docs）
```

每往下一层，数据生命周期越长、检索方式越复杂、更新频率越低。

**范围轴：**从全局到局部

```text
AGENTS.md -> 全局项目上下文，所有节点共享
memory 目录 -> 按 node_name 隔离，chat 和 gen_sql 互不干扰
workflow Context -> 单次 workflow 内共享，不同 workflow 完全隔离
sub-agent session -> ephemeral 纯内存，用完即销毁
```

### 为什么分四层而不是一个统一Memory 模块？

| 层 | 为什么不能合并 | 解决的问题 |
| --- | --- | --- |
| Prompt 层 | LLM 调用时“需要知道什么”和 prompt 构建强耦合，依赖模板渲染 | 注入逻辑 |
| SDK 层 | 对话历史由 OpenAI Agents SDK 管理，替换 SDK 需要整体替换 | 存在哪里、怎么压缩 |
| Workflow 层 | 多步任务的中间结果生命周期和 workflow 强绑定，workflow 结束即销毁 | 中间结果怎么传递 |
| 反思层 | 直接影响 workflow 结构，不只是记忆读写 | 结果出错怎么修正 |

每一层有自己的生命周期、读写频率、存储后端，分层后各自独立演进：换一个 session 存储方案不影响 Context 流转，改反思策略不影响对话持久化。

## 一、SDK 层：AdvancedSQLiteSession（对话持久化）

1. 1类与来源
agentic_node.py:20 导入了 OpenAI Agents SDK 内置的 session 机制：

```python
from agents.extensions.memory import AdvancedSQLiteSession
```

每个 AgenticNode 实例持有一个_session 属性和 session_id，通过 _get_or_create_session（） 懒初始化。

1. 2两种 Session 模式
agentic_node.py:507-535：

| 模式 | 触发条件 | 存储方式 | 适用场景 |
| --- | --- | --- | --- |
| 持久化模式 | ephemeral=False（默认） | model.create_session(session_id)，写入磁盘 SQLite | Chat 节点、顶层交互 |
| Ephemeral 模式 | ephemeral=True | AdvancedSQLiteSession(db_path=":memory:")，纯内存 | Sub-agent（子代理），用完即丢 |

```python
def _get_or_create_session(self):
    if self._session is None:
        if self.session_id is None:
            self.session_id = self._generate_session_id()
        if self.ephemeral:
            self._session = AdvancedSQLiteSession(
                session_id=self.session_id,
                db_path=":memory:",
                create_tables=True,
            )
        else:
            self._session = self.model.create_session(self.session_id)
    return self._session
```

1. 3 Session 存储路径
CLAUDE.md:86：

```text
~/.data_engineer/sessions/{project_name}/{session_id}.db
```

```text
~/.data_engineer/sessions/{project_name}/{session_id}.db
```

项目名从 os.getcwd（）派生，按项目隔离。不同项目的 session 互不干扰。

1. 4 自动Compaction（对话压缩）
当token 使用量逼近模型 context window 时，系统自动触发 compaction，将历史对话压缩为摘要写入 session。 agentic_node.py :244-258 提供了 context_length 属性动态读取当前模型的context window 大小，供 compaction 策略计算空间预算。

```python
@property
def context_length(self) -> Optional[int]:
    current = self.model
    if current is None:
        return None
    return current.context_length()
```

在 ChatAgenticNode.execute_stream（）的每次执行前会调用 await self._auto_compact（）检查是 否需要压缩。

## 二、Prompt 层：Memory Context 注入

2. 1memory_enabled 开关
agentic_node.py:101,152： 每个 AgenticNode 都有 memory_enabled 属性，控制是否在 system prompt 中注入 memory 片段。 每个 AgenticNode 都有 memory_enabled 属性，控制是否在 system prompt 中注入 memory 片段。

```python
self.memory_enabled: bool = (
    memory_enabled if memory_enabled is not None
    else has_memory(self.get_node_name())
)
```

默认规则（由 data_engineer.utils.memory_loader.has_memory() 决定）：

| 节点类型 | memory 默认 |
| --- | --- |
| chat | 开启 |
| 自定义 / user-defined subagent | 开启 |
| gen_sql / gen_report / feedback 等内置 subagent | 关闭 |

内置 subagent 关闭 memory 是为了保持 prompt 聚焦于当前任务，不被历史上下文干扰。

2. 2_inject_memory_context 流程
agentic_node.py:429-474：

1. 如果是 feedback 等特殊节点，允许 override_node_name 参数注入调用者的 memory（而非自身的）
2. 从
｛workspace_root｝/ .data_engineer/memory/ ｛node_name｝/ 目录加载 memory 内容

3. 通过 memory_context prompt 模板渲染后追加到 system prompt 末尾
```python
def _inject_memory_context(self, base_prompt, override_node_name=None):
    ...
```

```python
def _inject_memory_context(self, base_prompt, override_node_name=None):
    # feedback 路径无条件注入调用者的 memory
    if override_node_name:
        node_name = override_node_name
    else:
        if not self.memory_enabled:
            return base_prompt
        node_name = self.get_node_name()

    memory_content = load_memory_context(workspace_root, node_name)
    memory_dir = get_memory_dir(workspace_root, node_name)
    memory_section = get_prompt_manager(...).render_template(
        template_name="memory_context",
        has_memory=True,
        memory_content=memory_content,
        memory_dir=memory_dir,
    )
    return base_prompt + memory_section
```

2. 3 AGENTS.md 项目上下文
agentic_node.py:476-501： 除了 per-node memory，系统还会读取 ｛cwd｝/AGENTS.md 的前200行，作为 <project_context>注入 system prompt。这提供了项目级的长效上下文。

2. 4 System Prompt 最终组装顺序
_finalize_system_prompt() 的执行顺序：

1. Base prompt（模板渲染）
2. AGENTS.md 项目上下文
3. Skills XML（可用技能列表）
4. Memory context（节点级记忆）
5. Language directive（输出语言约束）

## 三、Workflow 层：Context（工作记忆）

3. 1 Context 模型
schemas/node_models.py : 493-564：

```python
class Context(BaseModel):
    sql_contexts: List[SQLContext]       # SQL 执行历史链
    table_schemas: List[TableSchema]    # Schema 缓存
    table_values: List[TableValue]      # 样本数据缓存
    metrics: List[Metric]               # 指标缓存
    doc_search_keywords: List[str]      # 文档检索关键词
    document_result: DocSearchResult    # 文档检索结果
    parallel_results: Dict              # 并行节点执行结果
    last_selected_result: Any           # Selection 节点选择结果
    selection_metadata: Dict            # Selection 元数据
```

Context 属于 Workflow 实例（workflow.py:51），随 workflow 生命周期存在。它充当一次 SQL 生成任务中的工作记忆，各 Node 通过 update_context()/setup_input() 读写它。

3. 2 SQLContext ——每轮SQL 的记忆单元
```python
class SQLContext(BaseModel):
    sql_query: str                  # 生成的 SQL
    explanation: str                # SQL 解释
    sql_return: Any                 # 执行结果（DataFrame/CSV）
    sql_error: str                  # 执行错误
    row_count: int                  # 返回行数
    reflection_strategy: str        # 反思采用的策略
    reflection_explanation: str     # 反思解释
```

Context.sql_contexts 是一个 List，按时间顺序追加。每次 SQL 生成 -> 执行 -> 反思 会新增一个 SQLContext。后续的 GenerateSQLNode 会将所有历史 sql_contexts 拼入 prompt，实现上下文延续和多轮修正。

3. 3 Context 在 Node 间的流转
```text
Node A setup_input()  ->  Node A 执行  ->  update_context()
                 \                         /
                  \-> workflow.context <-/
```

setup_input（Workflow）：从 workflow.context 读取上游结果，构造当前 Node 的 input。

update_context（Workflow）：将当前 Node 的 result 写回 workflow.context。

例如 ReflectNode.update_context() 会将反思策略和解释写回最后一个 SQLContext：

```python
last_record = workflow.context.sql_contexts[-1]
last_record.reflection_strategy = strategy
last_record.reflection_explanation = result.details.get("explanation", "")
```

## 四、反思层：ReflectNode + StrategyType

4. 1反思策略枚举
schemas/node_models.py :621-631：

```python
class StrategyType(str, Enum):
    SUCCESS = "SUCCESS"                      # SQL 执行正确，直接输出
    DOC_SEARCH = "DOC_SEARCH"                # 需要查文档
    SIMPLE_REGENERATE = "SIMPLE_REGENERATE"  # 简单重新生成
    SCHEMA_LINKING = "SCHEMA_LINKING"        # 重新做 Schema Linking
    REASONING = "REASONING"                  # 增强推理
    COLUMN_EXPLORATION = "COLUMN_EXPLORATION"# 探索列信息
    UNKNOWN = "UNKNOWN"                      # 无法判断
```

4. 2反思循环
reflect_node.py:89-126：

1. 每次 SQL 执行后，ReflectNode 调用 LLM评估结果
2. 根据评估建议的策略，动态向 workflow 中插入新节点
3. 有最大反思轮次限制（环境变量 MAX_REFLECTION_ROUNDS，默认 3）
```text
轮次 1：SIMPLE_REGENERATE -> 插入 regenerate 节点
轮次 2：SCHEMA_LINKING -> 插入 schema_linking 节点重新匹配表
轮次 3：REASONING -> 达到上限，强制执行推理节点
轮次 4：超出上限，强制终止
```

```text
反思策略会根据失败原因选择：重新生成、重新做 Schema Linking、增强推理或列探索。
```

```python
max_round = get_env_int("MAX_REFLECTION_ROUNDS", 3)
if workflow.reflection_round == max_round:
    return self._execute_strategy(details, workflow, StrategyType.REASONING)
elif workflow.reflection_round > max_round:
    return {"success": True, "message": "Max reflection rounds exceeded"}
```

```text
超过最大反思轮次后，workflow 不再继续插入修复节点，避免无限循环。
```

4. 3策略执行：动态 Workflow 调整
reflect_node.py:128-174： 反思不是简单的"再试一次"，而是动态向 workflow 插入新节点：

```python
for node_type in reflection_nodes:
    new_node = Node.new_instance(
        node_id=f"reflect_{workflow.reflection_round}_{node_type}",
        node_type=node_type,
    )
    workflow.add_node(new_node, current_position + 1)
```

这种设计让反思不仅是一条"记忆回路"，还是workflow 结构自我演化的驱动力。

## 五、ActionHistory：执行轨迹记录

5. 1模型
schemas/action_history.py:45-80：

```python
class ActionHistory(BaseModel):
    action_id: str
    role: ActionRole
    messages: str
    action_type: str
    input: Any
    output: Any
    status: ActionStatus
    start_time: datetime
    end_time: datetime
    depth: int
    parent_action_id: str
```

5. 2 ActionHistoryManager
集中管理所有 action 的生命周期，支持：

- 按action_id 索引查找
- 获取最后 N个 actions
- 序列化为 dict 用于持久化/展示
每次LLM 调用、工具调用、节点执行都生成对应的 ActionHistory 记录，形成完整的执行轨迹链。这不仅用于调试和 可观测性，也在 compact 时作为压缩源数据。

## 六、存储层：知识库的持久化记忆

除了运行时的 context/session 管理，Data Engineer Agent还有一套知识库（KB）持久化存储，可以理解为“长期记 忆"：

6. 1 存储模块（LanceDB 向量数据库）
data_engineer/storage/ 下的模块：

| 模块 | 内容 | 作用 |
| --- | --- | --- |
| schema_metadata | 表结构、字段、样本值 | Schema Linking 检索 |
| semantic_model | 指标/维度语义理解 | 语义模型定义 |
| metric | 指标定义、计算逻辑 | Metrics Search |
| ext_knowledge | 业务术语-SQL 映射 | 外部知识 |
| reference_sql | 参考 SQL 示例 | Few-shot 检索 |
| reference_template | SQL 模板 | 模板化 SQL 生成 |
| document | 平台文档（Snowflake/Polaris 等） | 文档 RAG |
| feedback | 用户反馈 | 反馈驱动的持续改进 |

6. 2 存储路径（按项目隔离）
```text
{project_root}/subject/
├── semantic_models/   # 语义模型 YAML
├── sql_summaries/     # SQL 摘要 YAML
└── ext_knowledge/     # 外部知识 CSV

~/.data_engineer/data/{project_name}/data_engineer_db/  # LanceDB 向量库
```

6. 3 RAG 检索流程
DocSearchNode 等节点会从 在 workflow 执行时， SchemaLinkingNode、SearchMetricsNode、 LanceDB 中检索相关内容注入Context，形成 检索增强的工作记忆。

## 七、完整流程示例

一次 SQL 生成任务中，memory/context 的完整流转：

```text
用户输入 -> BeginNode 初始化 workflow -> DateParserNode 解析相对时间
        -> SchemaLinkingNode 向量检索并写入 Context.table_schemas/table_values
        -> GenSQLAgenticNode 读取 Context、metrics、memory_context、AGENTS.md 后生成 SQL
        -> ExecuteSQLNode 执行 SQL 并写入 sql_return
        -> ReflectNode 评估结果，失败时动态插入修复节点
        -> OutputNode 输出最终结果
```

```text
1. 用户输入："上个月每个产品的销售额是多少？"
2. [BeginNode] 初始化 workflow，Context 创建（空）
3. [DateParserNode] 解析相对时间 -> "2026-04"，写入 SqlTask.date_ranges
4. [SchemaLinkingNode] 从 LanceDB 匹配相关表，写入 Context.table_schemas/table_values
5. [GenSQLAgenticNode] 读取 Context、metrics、memory_context、AGENTS.md，生成 SQL 并追加 Context.sql_contexts[0]
6. [ExecuteSQLNode] 执行 SQL，写入 Context.sql_contexts[0].sql_return
7. [ReflectNode] 评估结果：SUCCESS 则跳过；失败则选择策略并动态插入新节点，写回 reflection_strategy
8. [OutputNode] 输出最终结果，保存到 output_dir
9. Session 持久化：chat 模式下由 AdvancedSQLiteSession 保存对话历史
```

## 八、关键设计

1. Sub-agent 默认不启用 memory：内置 subagent （gen_sgl 等）聚焦单次任务，不受历史干扰；chat 节点和用
户自定义 subagent默认启用

2. Ephemeral vs 持久化 session:sub-agent 使用：memory：模式，不产生持久化开销；顶层交互持久化到
~/.data_engineer/sessions/

3. Memory 按 node_name 隔离：不同节点类型有独立的memory 目录，chat和 gen_sql 的 memory 互不干扰
4. AGENTS.md 作为全局项目上下文：所有节点共享，前200行注入prompt
5. Context 是 workflow 级别的：同一个 workflow 中的所有节点共享同一个 Context，但不同workflow 完全隔离
6. Reflection 有最大轮次限制：防止无限循环，默认 3轮后强制执行 reasoning 或终止

## 九、面试题

### Q1:Data Engineer Agent 的memory 架构分为哪几层？

**答：**四层。SDK 层用 AdvancedSQLiteSession 做对话持久化和自动 compact；Prompt 层按节点类型选择性注

入 memory 到 system prompt；Workflow 层用 Context.sql_contexts 做任务级工作记忆；反思层用 ReflectNode 评估结果并动态调整workflow。 AdvancedSQLiteSession 的Ephemeral 和持久化模式有什么区别？

### Q2

**答：**Ephemeral是：memory：纯内存模式，sub-agent 用完即丢，零磁盘开销；持久化模式写入

~/.data_engineer/sessions/ ｛project｝/ ｛session_id｝.db，chat 节点跨会话可恢复。两者的切换只靠 一个 ephemeral bool 标记。

### Q3：为什么 gen_sql 等内置 subagent默认 memory_enabled = False 而 chat 默认开

### 启？

**答：**内置 subagent 做原子任务（生成一条SQL），历史对话会干扰质量，而且 context window 要留给 schema、

metrics 等关键信息。chat 节点面向多轮交互，需要记忆上下文。

### Q4:Context.sql_contexts 的累积机制是怎样的？

**答：**每轮 SQL 生成-执行-反思后append 一个 SQLContext，包含SQL、执行结果、错误和反思策略。下一轮

GenerateSQLNode 把整条链拼入 prompt，LLM 能看到之前所有的 SQL 和错误，形成 in-context learning 链。 本质上是把"我的执行轨迹"变成了 few-shot 示例。

### Q5:ReflectNode 有哪些策略？如何防止无限循环？

**答：**7 种策略—— SUCCESS / SIMPLE_REGENERATE / SCHEMA_LINKING / DOC_SEARCH / REASONING /

COLUMN_EXPLORATION / UNKNOWN，分别对应不同失败原因。防死循环靠 MAX_REFLECTION_ROUNDS（默认

- 3）：第3轮强制执行 REASONING，第4 轮直接终止。

### Q6: Memory 注入 system prompt 的完整顺序是什么？

**答：**每次 prompt 构建走 _finalize_system_prompt()：base 模板 AGENTS.md 项目上下文（前200行）

> Skills XML > memory_context（仅 memory_enabled=True 的节点，从 ｛workspace｝/.data_engineer/memory/｛node_name｝/ 加载） -> 语言约束。整个过程按节点类型决定是否 注入 memory。

### Q7：为什么 sub-agent用 Ephemeral session 而不是持久化？

sessions/ 目录会快速膨胀，而且 sub-agent

**答：**sub-agent是临时执行单元，用完即销毁；如果每个都落盘，

内右 caccinn 面忡 面干净 的对汪历中不应运氿顶层 caccinn 的对话历史不应污染顶层 session。内存 session 更快、更干净。

### Q8: ActionHistory.depth 字段有什么用？

**答：**depth 标记嵌套层级（0=主流程，1=sub-agent）。compact 时优先压缩 depth>0 的子代理内部细节，保留

depth=0 的用户可见决策点，比纯按时间压缩更智能。

### Q9：如何给 Data Engineer Agent 增加”长期用户偏好记忆"？

**答：**最轻方案是利用现有 ｛workspace｝/.data_engineer/memory/｛node_name｝/ 目录放偏好文件，

_inject_memory_context 自动注入，零代码。进阶可以 LLM 自动提取偏好 >LanceDB 存储— 向量检索。

### Q10:Memory 系统的性能瓶颈在哪？

**答：**五处：长 session 文件加载慢（靠 compaction）；sql_contexts 撑爆 prompt（限制最近N个）；

LanceDB 大规模检索延迟（分层索引+缓存）；Memory 文件每次IO（mtime 检测+内存缓存）；ActionHistory 膨 胀（按 depth 裁剪）。

### Schema 语义检索引擎—混合检索系统 | 核心开发| 2026.01-2026.04

#### 项目背景

1. 数据工程场景中，Schema 信息散落在数据库 catalog、平台文档、历史 SQL 等多个来源，传统关键词检索无法
理解业务语义（如"用户下单金额"无法匹配到 orders.total_amount字段）。

2. 现有 RAG 检索方案大多依赖单一向量检索，缺乏关键词精确匹配能力，在 Schema 字段名这种需要精确命中的场
景下召回率不足，且检索延迟在千万级数据量下达到秒级，影响交互体验。

3. 我设计并实现了一套混合检索引擎，结合向量语义检索与 BM25 关键词匹配，覆盖 Schema 元数据、平台文档、
业务指标、参考 SQL 四类异构数据源，将 Schema 检索延迟从秒级降至毫秒级。

#### 我的工作

1. 基于 LanceDB 构建四层向量存储体系：SchemaWithValueRAG（表名/列名/类型/描述）、DocumentStore（平台
使用手册与最佳实践）、MetricRAG（业务指标到字段的映射，如GMV-orders.total_amount）、 ReferenceSqlRAG（历史优质 SQL 示例），各层独立索引、独立检索，通过统一门面接口对外暴露。

2. 实现 create_vector_index()预计算向量索引：数据量小于 5000行时采用IVF_FLAT（精度优先），超过5000
行自动切换IVF_PQ（压缩优先，内存占用降低 70%），向量维度384维，兼顾检索质量（recall@10> 0.95） 和存储开销（单条约 1.5KB）。DocumentStore 的 store_chunks 采用 delete-then-add 策略替代 merge_insert，避免 LanceDB 的 commit conflict 问题。

3. 设计 OptimizedRecall 混合检索策略，BM25关键词检索与向量语义检索并行执行，通过多字段加权融合：
vector_score × 0.5（语义相似度）+bm25_score × 0.3（关键词精确匹配）+title_boost×0.1（表名/字段名命中加 权）+hierarchy_boost×0.05（父子表层级关系加权）+keywords_boost × 0.05（人工标注关键词加权）。融合后 引入 DiversityScorer 多样性约束，避免 Top-K 结果集中在单一表的多个字段上。

4. 实现 QueryExpander 同义词扩展模块、维护业务术语到字段名的同义词映射表（如"下单金额"自动扩展为［"订单
金额”，“支付金额"，"total_amount”，"order_amount"］），同时通过向量相似度自动发现候选同义词（cosine similarity > 0.85），双路保障下召回率进一步提升 15%。

5. 在benchmark测试集上完成混合检索策略的多轮对比实验，验证加权融合公式各参数的最优配比和
DiversityScorer 多样性阈值的有效性。

#### 项目成果

1. 检索 F1 从 0.71提升至 0.89，绝对提升 0.18，相对提升 25%；Top-5 准确率从 65% 提升至 82%。
2. Schema 检索延迟从1.2s 降至120ms，降幅90%，支持千万级向量实时查询。
3. 召回率提升 15%：Query 扩展覆盖同义词和业务术语变体。
4. 统一检索覆盖4类异构数据源（Schema 元数据、平台文档、业务指标、参考 SQL），消除多系统切换成本。

### SQL 生成引擎—多节点工作流编排|核心开发| 2026.01-2026.04

#### 项目背景

1. 数据工程师每天编写大量 ETL SQL，传统方式平均每条查询耗时 30 分钟以上，且跨数据库方言迁移（如
PostgreSQL -> Snowflake）需要重写，错误率高达 30%。

2. 现有 NL2SQL 方案多为单轮生成，缺乏系统化的验证和纠错机制，SQL 语法/逻辑错误无法自动修复，仍需人工
介入。

3. 我设计并实现了一个支持11种数据库方言的 SQL 生成引擎，构建了验证-分析-修复的反思闭环，将自然语言自动转化为准确 SQL。

#### 我的工作

1. 设计多节点工作流编排架构，将 SQL 生成流程分解为 Begin（初始化） -> Selection（意图分类） ->
SchemaLinking（表结构检索） -> GenSQL（LLM 生成） -> Reflect（错误分析） -> Fix（SQL 修复） -> Execute（执行验证） -> Output（结果输出）等独立阶段，各节点通过 Workflow 统一按拓扑序调度，节点间通过 SqlTaskState 传递数据，实现松耦合。

2. 采用工厂模式管理节点生命周期，通过 Node.new_instance()工厂方法根据node_type 动态创建节点，新增节点
只需添加 case 分支，不破坏现有代码，符合开闭原则。

3. 实现 GenSQLAgenticNode，内部集成 Prompt 构建、LLM 调用、SQL 解析三步。通过 few-shot learning 注入
top_k=3 个最相关的参考 SQL 示例，提升生成质量。

4. 设计反思机制（ReflectNode + FixNode）实现验证-分析-修复的闭环：语法错误由 SQLGlot 做语法解析验证，列
名错误由 Schema 对比检测，逻辑错误由 LLM 反思。ReflectNode 分类错误原因，FixNode 针对不同错误类型调用 LLM 修复，最大反思轮次限制为 3 次，通过 reflection_round >= 3 和 "unknown table" 等终止条件防止无限循环。85% 的常见语法错误可通过反思自动修复。

5. 设计基于查询复杂度的模型路由策略：简单查询（单表 SELECT、聚合等）路由至 GPT-4.1-mini 以降低延迟和成本，复杂查询（多表 JOIN、子查询、窗口函数）路由至 GPT-4o 以保证生成质量。结合 Prompt 压缩（去除冗余 指令、精简 few-shot 示例），LLM Token 成本降低 60%。

6. 定义 SqlTaskState 作为工作流状态载体（task_id、nl_query、datasource、target_tables、generated_sql、
result），TableInfo 建模表名/列信息/描述/行数，ColumnInfo 建模列名/类型/约束。Context 类管理会话上下文， 支持多会话并发。

#### 项目成果

1. SQL 语法错误自动修复率达 85%，反思机制覆盖大部分常见语法错误，减少人工介入频次。
2. 支持 11 种数据库方言：PostgreSQL、MySQL、Snowflake、StarRocks、ClickHouse 等全覆盖。
3. LLM Token 成本降低 60%：Prompt 压缩 + 模型路由，简单查询用小模型。
4. 查询编写效率提升 10 倍以上，自然语言输入替代手动 SQL 编写。
