# 简历模板、八股文、技术面 QA

> **文档编号：** 15_Data_engineer-Agent_简历,八股,技术面

> **使用提醒：** 简历中的内容都是参考材料。按自己真正学会的深度写进简历,怎么方便面试怎么来; 项目不一定要全学会,来不及时把已经掌握的部分写上即可,灵活变通。

## 目录

- Data_engineer 项目简历
- 项目简历内容
- STAR 法则完整示例
- 简历写法 + STAR 法则指南
- 面试问答精编
- 技术面总结

## Data_engineer 项目简历

### 项目简介

Data_engineer 是一个数据工程智能体平台,通过自然语言处理和语义检索,将用户的自然语言查询转换为准确的 SQL 语句。我基于多节点工作流编排 设计并实现了整个系统,支持 10+ 种 LLM 提供者和 11 种数据库,通过持续学习构建进化的知识上下文,显著提升 SQL 生成准确率。

### 核心功能

- 自然语言转 SQL:NL → 意图理解 → 语义检索 → SQL 生成
- Evolvable Context:构建活的知识库,捕获 schema 元数据、参考 SQL、语义模型、指标
- 多数据库支持:内置 SQLite/DuckDB + PostgreSQL、MySQL、Snowflake、StarRocks 等适配器
- 多 LLM 支持:OpenAI、Claude、Gemini、DeepSeek、Qwen 等 10+ 提供者
- Subagent 封装:将成熟领域封装为 scoped chatbot,通过 API/Web/MCP 交付
- 语义层集成:通过 MetricFlow 集成定义业务指标,生成跨方言 SQL
- MCP 协议:既是 MCP Server 暴露工具,也是 MCP Client 消费外部工具

### 技术栈

沿用到skill, herness

## 项目简历内容

### Python/AI工程师版本

2026.01 - 2026.04 | Data_engineer 数据工程智能体 | 核心开发

### 项目背景

数据工程师在构建 ETL 流程时面临挑战:传统方式需要手动编写大量 SQL,且难以处理跨数据库方言差异。一次跨方言迁移平均需要 2-3 天,且错误率高达 30%。我设计并实现了一个智能的数据工程助手,通过自然语言和语义检索,自动生成准确的 SQL 语句,并支持业务指标的语义层抽象。

### 主要负责

**架构设计：** 我设计了基于多节点工作流编排的 SQL 生成系统,将查询流程分解为意图分类(BeginNode → SelectionNode)、Schema 链接 (SchemaLinkingNode)、上下文检索、LLM 生成(GenSQLAgenticNode)、执行验证(ExecuteSQLNode)、结果输出(OutputNode)等独立阶段,每个阶段由专门的 Node 节点处理,通过有向无环图(DAG)实现灵活的流程编排,支持条件分支和并行执行。架构上采用工厂模式管理节点生命周期,通过 Node.new_instance() 工厂方法根据 node_type 动态创建节点,新增节点只需添加 case 分支,不破坏现有代码,符合开闭原则。

**关键实现 — 向量检索系统：** 我实现了基于 LanceDB 的向量检索系统,支持 Schema 元数据、平台文档、参考 SQL 的语义搜索。通过 create_vector_index() 方法预计算向量索引(数据量小于 5000 行时用 IVF_FLAT,超过时自动切换 IVF_PQ),将 Schema 检索延迟从秒级(1.2s) 降低到毫秒级(120ms),降幅达 90%。向量维度采用 384 维( get_document_embedding_model ),兼顾检索质量和存储开销。

**关键实现 — 混合检索策略：** 我设计了混合检索策略(BM25 + 向量检索),将关键词精确匹配与语义相似度搜索结合。通过多字段加权 (vector_score×0.5 + bm25_score×0.3 + title_boost×0.1 + hierarchy_boost×0.05 + keywords_boost×0.05)和多样性约束( DiversityScorer ), 显著提升检索结果的相关性和覆盖度。在 benchmark 测试集上,检索 F1 从 0.71 提升到 0.89,提升 25%;Top-5 准确率从 65% 提升到 82%。Query 扩展模块( QueryExpander )支持同义词扩展,进一步提升召回率 15%。

**关键实现 — SQL 生成与反思：** 我实现了 GenSQLAgenticNode ,内部集成 Prompt 构建、LLM 调用、结果解析三步。通过 few-shot learning 注入 top_k=3 个最相关的参考 SQL 示例,提升生成质量。反思机制( ReflectNode + FixNode )实现验证-分析-修复的闭环:语法错误(SQLGlot 验证)、列名错误(Schema 对比)、逻辑错误(LLM 反思)分类处理,85% 的常见语法错误可通过反思自动修复。最大反思轮次限制为 3 次,防止无限循环。

**数据建模：** 我定义了  SqlTaskState 作为工作流状态载体,包含 task_id、nl_query、target_tables、generated_sql、result 等字段。Schema 信息建模为 TableInfo (表名、列、描述)和 ColumnInfo (列名、类型、约束)。 Context 类管理会话上下文,支持多会话并发。

### 项目成果

- 检索准确率提升 25%:F1 从 0.71 提升到 0.89,Top-5 准确率从 65% 提升到 82%
- Schema 检索延迟降低 90%:从 1.2s 降至 120ms,支持千万级向量实时查询
- SQL 语法错误自动修复率 85%:反思机制覆盖大部分常见语法错误
- 支持 11 种数据库:PostgreSQL、MySQL、Snowflake、StarRocks、ClickHouse 等全覆盖
- LLM Token 成本降低 60%:Prompt 压缩 + 模型路由,简单查询用 GPT-4.1-mini,复杂查询用 GPT-4o

### 技术架构

```text
  1 用户查询 → CLI/API → Agent → Workflow → Node Graph
  2             ├→ BeginNode
  3             ├→ SchemaLinkingNode
  4             ├→ GenSQLAgenticNode
  5             │  ├→ _build_prompt()
  6             │  ├→ _retrieve_context()
  7             │  ├→ _call_llm()
  8             │  ├→ _parse_sql()
  9             │  └→ _verify_sql()
  10            ├→ ExecuteSQLNode
  11            └→ OutputNode

```

```text
  13 Storage Layer:
  14 LanceDB (向量) ← SchemaWithValueRAG (Schema元数据)
  15      ← DocumentStore (平台文档)
  16      ← MetricRAG (业务指标)
  17      ← ReferenceSqlRAG (参考SQL)

```

```text
  19 混合检索:
 20  BM25 (关键词) ─┐
  21      ├→ 加权融合 → DiversityScorer → Top-K
 22  向量 (语义) ──┘

```

## STAR 法则完整示例

### S(背景,15%)

数据工程师团队每天需要编写大量 ETL SQL,传统方式依赖人工理解表结构和业务语义。平均每个查询耗时 30 分钟以上,跨数据库方言(如 PostgreSQL → Snowflake)的 SQL 迁移需要重写,且错误率高达 30%。此外,Schema 文档散落在各处,更新不及时导致生成的 SQL 与实际表结构不符。

### T(任务,15%)

1. 实现自然语言到 SQL 的自动转换,减少人工编写时间
2. 构建 Schema 语义检索系统,解决表结构理解难题
3. 支持多数据库方言的 SQL 生成,提升复用率
4. 建立反思验证机制,降低生成 SQL 的错误率

### A(行动,50%)

**架构设计：** 我设计多节点工作流编排架构,将 SQL 生成流程分解为 Begin(初始化)→ Selection(意图分类)→ SchemaLinking(表结构检索)→ GenSQL(LLM 生成)→ Execute(执行验证)→ Output(结果输出)等独立节点,各节点通过 Workflow 统一调度。 Workflow 管理 nodes 字典 和 node_order 列表,执行时按拓扑序调用各节点的 execute() 方法。节点间通过 SqlTaskState 传递数据,不直接调用其他节点的内部状态,实现松耦合。

**关键实现 — 向量检索：** 我实现 SchemaWithValueRAG 存储层,基于 LanceDB 向量数据库存储表结构描述。通过 create_vector_index() 创建 IVF_PQ 索引(超过 5000 行自动切换),将平均检索延迟从 1.2s 降至 120ms。 DocumentStore 的 search_docs 方法支持多版本管理和增量更新, store_chunks 使用 delete-then-add 策略避免 merge_insert 的 commit conflict。

**关键实现 — 混合检索：** 我设计 OptimizedRecall 类实现 BM25 + 向量的混合检索。通过多字段加权(vector×0.5 + bm25×0.3 + title×0.1 + hierarchy×0.05 + keywords×0.05)和多样性约束,检索 F1 从 0.71 提升到 0.89。Query 扩展支持同义词,将召回率进一步提升 15%。

**关键实现 — 反思机制：** 我设计 ReflectNode 分析错误原因(语法错误 / 列名不存在 / 逻辑不合理), FixNode 针对不同错误类型调用 LLM 修复, HITLNode 作为兜底人工介入。 GenSQLAgenticNode 的 _should_continue_reflection 方法通过 reflection_round >= 3 和 "unknown table" 等 条件防止无限循环。85% 的常见语法错误可通过反思自动修复。

**数据建模：** 我定义 SqlTaskState 作为工作流状态载体,包含 task_id、nl_query、datasource、target_tables、generated_sql、result 等字段。 TableInfo 建模表名、列信息、描述、行数; ColumnInfo 建模列名、类型、约束。

### R(结果,20%)

- 检索 F1 提升 25%:从 0.71 到 0.89,Top-5 准确率从 65% 到 82%
- Schema 检索延迟降低 90%:从 1.2s 到 120ms,支持千万级向量实时查询
- SQL 语法错误自动修复率 85%:反思机制覆盖大部分常见语法错误
- 支持 11 种数据库:PostgreSQL、MySQL、Snowflake、StarRocks、ClickHouse 等全覆盖
- LLM Token 成本降低 60%:Prompt 压缩 + 模型路由,简单查询用小模型

## 简历要点(可复用)

1. 设计并实现基于多节点工作流编排的 SQL 生成系统,将自然语言查询转换为可执行 SQL,涵盖意图分类、Schema 链接、LLM 生成、执行验证等阶段,检索 F1 提升 25%
2. 实现基于 LanceDB 的向量检索系统,通过预计算索引将 Schema 检索延迟从秒级降至毫秒级(120ms),降幅达 90%
3. 设计混合检索策略(BM25 + 向量检索),通过多字段加权和多样性约束,F1 从 0.71 提升到 0.89
4. 构建可扩展的存储抽象层,统一管理 Schema 元数据、业务指标、参考 SQL 等多种存储后端,通过工厂模式支持 11 种数据库适配器
5. 实现 SQL 反思验证机制,85% 的语法错误可通过反思自动修复

## Data_engineer - 简历写法 + STAR 法则指南

## 一、简历项目经历模板

### 模板 A:数据工程  / NL2SQL(AI 工程师)

- 设计并实现基于多节点工作流编排的 SQL 生成系统,将自然语言查询转换为可执行 SQL,涵盖意图分类、Schema 链接、LLM 生成、执行验证等阶段
- 实现基于 LanceDB 的向量检索系统,支持 Schema 元数据、平台文档、参考 SQL 的语义搜索,预计算向量索引将检索延迟从秒级降至毫秒级
- 设计混合检索策略(BM25 + 向量检索),通过多字段加权(title、hierarchy、keywords)和多样性约束,检索 F1 从 0.71 提升至 0.89
- 构建可扩展的存储抽象层,统一管理  Schema 元数据、业务指标、参考 SQL 等多种存储后端,通过工厂模式和策略模式支持 11 种数据库适配器
- 实现 SQL 反思验证机制,语法错误自动修复率达 85%,减少人工介入次数

### 模板 B:MCP 协议集成  / 工具生态

- 实现 MCP Server 暴露工具给 Claude Desktop、Cursor 等 IDE,支持一键接入 AI 辅助编程工作流
- 设计 Skills 打包工具系统,支持可配置权限管理和市场集成(agentskills.io 风格),降低用户扩展成本
- 优化 MCP 工具注册机制,支持动态加载和按需激活,减少冷启动时间 40%

### 模板 C:API 服务 / 后端架构

- 开发 FastAPI REST API 服务,支持 Chat、Agent、Database、Tool 等核心业务路由,QPS 支撑 100+
- 设计会话管理系统,基于 SQLite 本地存储实现多会话并发管理,支持会话历史导出和导入
- 实现数据库连接池管理和重试机制,支持  DuckDB、PostgreSQL、MySQL 等 11 种数据库的透明切换

## 二、STAR 法则详解

### STAR 定义表格

### STAR 完整示例

S(背景,2-3 句话): 数据工程团队每天需要编写大量 ETL SQL,传统方式依赖人工理解表结构和业务语义,平均每个查询耗时 30 分钟以上,且跨 数据库方言(如 PostgreSQL → Snowflake)的 SQL 迁移需要重写。

### T(任务,3-4 个目标)

1. 实现自然语言到 SQL 的自动转换,减少人工编写时间
2. 构建 Schema 语义检索系统,解决表结构理解难题
3. 支持多数据库方言的 SQL 生成,提升复用率
4. 建立反思验证机制,降低生成 SQL 的错误率

### A(行动,按四段展开)

**架构设计：** 设计多节点工作流编排架构,将 SQL 生成流程分解为 Begin(初始化)→ Selection(意图分类)→ SchemaLinking(表结构检索)→ GenSQL(LLM 生成)→ Execute(执行验证)→ Output(结果输出)等独立节点,各节点通过 Workflow 统一调度,支持条件分支和并行执行。

**关键实现：** 实现 SchemaWithValueRAG 存储层,基于 LanceDB 向量数据库存储表结构描述,通过预计算的 embedding 索引实现毫秒级 Schema 检索。 GenSQLAgenticNode 内部集成 Prompt 构建、LLM 调用、结果解析三步,通过 few-shot learning 注入参考 SQL 示例提升生成质量。

**难点攻克：** SQL 语法错误和逻辑错误是生成质量的主要瓶颈。通过设计反思机制——  ReflectNode 分析错误原因(语法错误 / 列名不存在 / 逻辑不合理), FixNode 针对不同错误类型调用 LLM 修复, HITLNode 作为兜底人工介入。测试显示 85% 的语法错误可通过反思自动修复。

**数据建模：** 定义 SqlTaskState 作为工作流状态载体,包含 task_id、nl_query、target_tables、generated_sql、result 等字段。Schema 信息建模为 TableInfo (表名、列、描述)和 ColumnInfo (列名、类型、约束)。

### R(结果,5 个量化指标)

- 检索 F1 提升 25%:混合检索策略使 benchmark 准确率从 0.71 提升到 0.89
- Schema 检索延迟降低 90%:预计算向量索引将平均延迟从 1.2s 降至 120ms
- SQL 语法错误自动修复率 85%:反思机制覆盖大部分常见语法错误
- 支持 11 种数据库:PostgreSQL、MySQL、Snowflake、StarRocks、ClickHouse 等全覆盖
- 会话管理 100+ 并发:SQLite 本地存储支撑多用户并发会话

## 三、面试常见追问与回答策略

### Q1: "这个项目的架构是怎么设计的?"

> **回答策略：** 从用户请求入口讲起,按数据流经过的模块依次展开,最后回到输出。重点讲为什么这样分层(解耦、可测试、可扩展)。

### Q2: "Schema 链接具体怎么做的?"

> **回答策略：** 讲清楚向量检索的流程(query → embedding → ANN 检索 → 结果解析),重点讲如何解决"表太多怎么筛"的问题(top_k 限制 + 字段过滤)。

### Q3: "反思机制是怎么设计的?"

> **回答策略：** 从验证失败的类型入手(语法  / 逻辑 / 超时),分别讲对应的修复策略。重点讲如何避免无限循环(max_reflection_round 限制)。

### Q4: "如果向量检索召回不准确怎么办?"

> **回答策略：** 从多个维度回答:chunking 策略优化(语义分块)、embedding 模型选择(中文 bge-large-zh)、混合检索补充关键词信号、rerank 二次排

序。

### Q5: "这个项目最大的技术难点是什么?"

> **回答策略：** 诚实回答 SQL 生成质量本身——LLM 的幻觉问题无法彻底消除,反思机制只能覆盖常见错误。真正的难点在于平衡召回率和精确率。

## 四、简历避坑指南

错误示范  vs 正确示范

### 四条原则

1. 动词开头:设计、实现、优化、搭建、构建
2. 量化优先:提升 X%、降低 Xms、支持 N 种
3. 技术具体:不写"AI 技术",写"RAG"、"向量检索"
4. 突出个人:不用"我们",用"我设计"、"我实现"

## 五、不同岗位的简历侧重

## Data_engineer - 面试问答精编(30+)

每题含:问题、参考答案(约  200~300 字量级)、面试官想听的点、常见踩坑。

## 类别一:项目整体设计

### Q1. 项目的整体架构是什么样的?

**参考答案：** 是一个基于工作流编排的数据工程智能体。用户通过 CLI 或 API 发起查询请求,请求首先进入 Agent 类,由 Workflow 管理执行流程。 Workflow 由多个 Node 节点组成,节点按预设顺序执行(Begin → Selection → SchemaLinking → GenSQL → Execute → Output)。 核心处理引擎在 datus/agent/node/ 目录,存储层在 datus/storage/ 。存储层使用 LanceDB 向量数据库,抽象出 BaseEmbeddingStore 基类, 其下有 DocumentStore (文档检索)、 SchemaWithValueRAG (Schema 元数据)、 MetricRAG (业务指标)等子类。

> **面试官想听的点：** 分层清晰、模块职责明确、能画出架构图、Node 工厂模式

> **常见踩坑：** 只讲技术栈不讲架构,或把架构说成"一个 Agent 处理所有请求"——说明没有理解节点拆分的设计。

### Q2. 为什么选择工作流节点编排而不是纯 Agent 模式?

**参考答案：** 纯 Agent 模式(如 AutoGPT)的优点是灵活,但缺点是调试困难、成本高、延迟大。SQL 生成流程中大部分步骤是确定性的:Schema 链接、执行验证的逻辑是固定的,不需要 LLM 动态决策。

采用"结构化 Workflow + AgenticNode"的混合模式 + AgenticNode"的混合模式: Workflow 固定执行顺序保证可预测性, GenSQLAgenticNode 内部通过 LLM 驱动生成和反思,保证灵活性。这兼顾了效率和能力。

> **面试官想听的点：** 理解 Workflow 和 Agent 的权衡、能说清楚各自适用场景、工程化思维

> **常见踩坑：** 说"因为纯 Agent 太慢了"——这是结果不是原因,应该从架构层面分析。

### Q3. 为什么不用 LangGraph 或 CrewAI?

**参考答案：** LangGraph 和 CrewAI 是通用 Agent 框架,不针对 SQL 生成场景定制。本项目从第一天就围绕 NL2SQL 场景设计:

1. 内置 SchemaLinkingNode ,不需要自己接入 Schema 检索
2. 内置 ExecuteSQLNode ,实际执行 SQL 验证结果
3. 内置 11 种数据库适配器,覆盖主流 BI 场景
4. MetricFlow 集成,支持业务指标的语义层抽象

MCP(Model Context Protocol)是 Anthropic 提出的标准,让 AI 与外部工具交互有统一规范。本项目实现 MCP 的价值:

> **面试官想听的点：** 对竞品有了解、能讲清楚差异化价值、场景驱动技术选型

> **常见踩坑：** 说"因为这是我们自己的项目"——这是主观原因,应该从功能差异角度分析。

### Q4. Node 节点是如何管理的?

**参考答案：** 通过工厂模式管理: Node.new_instance() 根据 node_type 参数创建对应节点子类。节点类型定义在 datus/configuration/node_type.py ,工厂 映射在 datus/agent/node/node.py:new_instance() 方法中。 每个 Node 有唯一 ID 和 description,通过 Workflow.add_node() 加入工作流。 Workflow 维护 nodes 字典和 node_order 列表,执行时按 node_order 顺序调用各节点的 execute() 方法。

> **面试官想听的点：** 工厂模式、节点可插拔、执行顺序控制

> **常见踩坑：** 说"每个请求都 new 一个 Node"——实际上节点是共享复用的。

### Q5. 新增一个节点需要改几个文件?

**参考答案：** 需要改 3 个文件:

1. datus/agent/node/my_node.py — 创建节点类,继承 Node ,实现 execute() 方法
2. datus/configuration/node_type.py — 添加 MY_NODE = "my_node" 类型常量
3. datus/agent/node/node.py:new_instance() — 添加 my_node.py 的 import 和 case 分支

这样新增节点完全不影响现有节点和其他模块,符合开闭原则。

> **面试官想听的点：** 开闭原则、工厂模式、新人能否快速上手

> **常见踩坑：** 说"需要改 Workflow 类"——这违反了开闭原则,说明设计有问题。

### Q6. 为什么需要 MCP 协议?

**参考答案：** MCP(Model Context Protocol)是 Anthropic 提出的标准,让 AI 与外部工具交互有统一规范。本项目实现 MCP 的价值:
1. 生态集成:Claude Desktop、Cursor 等 IDE 原生支持 MCP,一行配置就能接入本项目的工具能力
2. 双向通信:本项目既是 MCP Server(暴露工具),也是 MCP Client(消费外部工具)
3. 标准化:不用自己实现工具注册、发现、调用协议,降低开发成本

实际使用中,用户在 Claude Desktop 配置 mcpServers 后,可直接通过自然语言调用本项目的 SQL 生成、文档检索等工具。

> **面试官想听的点：** MCP 协议理解、生态意识、双向集成

> **常见踩坑：** 说"MCP 就是让 AI 调用工具"——太浅,应该从协议层和生态角度讲。

## 类别二:核心难点    — 并行与性能

### Q7. 向量检索的性能瓶颈在哪里?

**参考答案：** 向量检索的性能瓶颈主要在三个环节:
1. Embedding 生成:单次请求 20-50ms,主要消耗在 GPU 推理。本项目使用 get_document_embedding_model() 获取模型,batch_size 默认 32。
2. ANN 检索:LanceDB 默认 IVF_FLAT,1000 行以内数据直接暴力搜索;超过 5000 行自动切换 IVF_PQ。本项目的优化在 create_vector_index() 方法中根据数据量选择索引类型。

3. 结果解析:返回大量行时网络传输和序列化耗时。

**优化思路：** 预计算 + 批量查询 + 索引分区。本项目的 Schema 预加载和 StreamingDocProcessor 的并行处理都是这类优化。
> **面试官想听的点：** 能定位具体瓶颈点、懂 ANN 算法选择依据、知道优化方向

> **常见踩坑：** 说"向量检索很快不需要优化"——说明没有遇到过性能问题。

### Q8. 如何优化 LLM 的 Token 消耗?

**参考答案：** Token 消耗主要在 Prompt 构建和生成输出两个环节。本项目的优化策略:
1. Prompt 压缩: GenSQLAgenticNode 只注入相关的 Schema(按 target_tables 过滤),而不是全量 Schema
2. Few-shot 精简:参考 SQL 只取 top_k=3 个最相关的,不是无限注入
3. 结果缓存:相同 query 的生成结果可以缓存,避免重复 LLM 调用
4. 模型路由:简单查询用小模型(GPT-4.1-mini),复杂查询用大模型(GPT-4o)

**实际成本：** 一次 SQL 生成平均消耗 500-800 Token input + 200-400 Token output,相比直接用 GPT-4o 生成完整 ETL 管道代码节省 60%+。
> **面试官想听的点：** 成本意识、缓存策略、模型分级

> **常见踩坑：** 说"没有考虑过 Token 成本"——说明没有生产环境经验。

### Q9. 并行执行的状态冲突如何解决?

**参考答案：** 本项目在 StreamingDocProcessor 中使用 ThreadPoolExecutor 并行处理多个文档,状态冲突通过两种方式解决:

1. 不可变结果:每个线程返回独立的 FetchedDocument 对象,不修改共享状态
2. 线程安全统计: ProcessingStats 用 threading.Lock 保护计数器

```text
  1 stats.increment(docs=1, chunks=len(chunks)) # 线程安全

```

如果涉及写操作(如结果合并),使用  with self._lock: 保护临界区。Python 的 GIL 在 I/O 密集型场景下不影响性能。

> **面试官想听的点：** 线程安全实现、锁粒度选择、GIL 理解

> **常见踩坑：** 说"用全局变量共享状态"——这会导致竞态条件。

### Q10. 缓存一致性问题如何处理?

**参考答案：** 本项目使用 delete-then-add 而非 merge_insert 处理缓存一致性。原因:merge_insert 在并发写入时可能出现 commit conflict,而 delete-then-add 先删后加是原子操作。

```text
  1 # 删除已有 chunk
  2 self.table.delete(in_("chunk_id", batch_ids))
  3 # 写入新 chunk
  4 self.store_batch(data)

```

对于 Schema 元数据缓存,由于是预计算数据(不会在运行时修改),直接用 lru_cache 缓存实例,不存在一致性问题。

> **面试官想听的点：** 事务理解、并发意识、缓存策略选择

> **常见踩坑：** 说"直接覆盖写入"——这可能导致数据丢失或不一致。

## 类别三:核心难点    — 循环与流程控制

### Q11. 反思机制是如何设计的?

**参考答案：** 反思机制是多轮验证-修复循环:
1. 验证阶段( GenSQLAgenticNode._verify_sql ):语法检查用 SQLGlot,逻辑检查用 LLM 反思
2. 错误分析( ReflectNode ):分类错误类型——语法错误(缺少括号)、列名错误(表里没这列)、逻辑错误(WHERE 条件不合理)
3. 修复阶段( FixNode ):针对错误类型调用 LLM 生成修复后的 SQL
4. 终止条件: reflection_round >= 3 或人工触发 HITL

代1 码块if not is_valid:

```text
  2  state.reflection_needed = True
  3  state.error = error
  4  state.reflection_round += 1

```

> **面试官想听的点：** 状态机思维、错误分类、终止条件设计

> **常见踩坑：** 说"反思就是让 LLM 重新生成一次"——没有理解验证-分析-修复的闭环。

### Q12. 如何防止无限循环?

**参考答案：** 本项目通过三重保护防止无限循环:

1. 最大反射次数: reflection_round >= 3 强制终止
2. 超时机制: ExecuteSQLNode 设置 30s 执行超时
3. 人工兜底: HITLNode 作为最后一道防线,将问题转给人工

```text
  1 if state.reflection_round >= 3:
  2  state.status = "max_reflection_reached"return state # 跳出循环

```

> **面试官想听的点：** 防御性编程、多层保护、设计优先级

> **常见踩坑：** 说"理论上不会无限循环"——应该讲清楚实际的保护机制。

### Q13. 如果所有反思都失败了怎么办?

**参考答案：** 触发 HITL(Human-In-The-Loop)机制:系统不再尝试自动修复,而是将问题、降级后的 SQL 选项、错误日志打包,通过 HITLNode 暂停工作流, 等待人工决策。 用户可以通过 CLI 查看失败详情,选择:1)接受部分正确的 SQL 手动修改;2)提供更详细的上下文;3)放弃本次查询。 这个设计符合工程实践——不是所有问题都要自动解决,明确系统边界更重要。

> **面试官想听的点：** 工程边界意识、用户体验设计、容错降级

> **常见踩坑：** 说"会一直重试直到成功"——这会导致无限循环,是严重的设计缺陷。

## 类别四:工程化

### Q14. 如何保证代码质量?

**参考答案：** 本项目通过多层次保证代码质量:
1. 静态检查:Ruff (format + lint) 在 pre-commit 时运行,E/W/F/B/I/C90 规则覆盖
2. 类型检查:使用完整 type hint + mypy 检查
3. 单元测试: tests/unit_tests/ 目录下每个模块有对应测试,CI 级别测试覆盖率要求 80%+
4. diff coverage:不仅看整体覆盖率,还要求新增代码 80%+ 有对应测试
5. 代码审查:PR 必须经过 review,Commit Message 有格式要求([Feature]/[BugFix]/[Refactor] 等前缀)

```text
  1 uv run pytest tests/unit_tests/ --cov=datus --cov-fail-under=80
  2 uv run diff-cover coverage.xml --compare-branch=upstream/main --fail-under=80

```

> **面试官想听的点：** 测试覆盖率意识、自动化流程、代码规范

> **常见踩坑：** 说"我们主要靠人工 review"——没有自动化测试的项目不可维护。

### Q15. Schema 演进如何处理?

**参考答案：** Schema 演进(表结构变更)通过 CDC 模式处理:
1. 初始化: init_local_schema() 扫描数据库表结构,生成 embedding 存入 LanceDB
2. 变更检测:通过文件 hash 对比判断 Schema 是否变化
3. 增量更新:变化时删除旧 Schema,重新计算 embedding

```text
  1 # 增量更新逻辑if compute_hash(new_schema) != stored_hash:
  2  delete_old_schema(doc_path)
  3  store_new_schema(new_schema)

```

> **面试官想听的点：** 版本管理意识、增量更新思维

> **常见踩坑：** 说"每次都全量重新加载"——这在大表场景下不可接受。

### Q16. 日志和可观测性如何设计?

**参考答案：** 本项目使用统一的日志规范:

1. 日志框架:通过 get_logger(name) 获取 logger,格式化统一
2. 日志级别:INFO(正常流程)、WARNING(非致命问题)、ERROR(需要关注的问题)
3. 结构化日志:包含 task_id、node_id 等上下文字段,方便排查

```text
  1 logger = get_logger(__name__)
  2 logger.info(f"Processed {stats.total_docs} docs, {stats.total_chunks} chunks")

```

追踪方面,使用 optional_traceable 装饰器支持链路追踪注入。关键指标:检索延迟、SQL 生成成功率、执行时间等通过 ProcessingStats 统计。

> **面试官想听的点：** 日志规范意识、上下文埋点、关键指标

> **常见踩坑：** 说"用 print 调试"——生产环境不能用 print。

### Q17. 密钥管理如何处理?

**参考答案：** 本项目的密钥管理原则:

1. 不硬编码:API Key 存储在环境变量或 agent.yml ,使用 ${ENV_VAR} 语法引用
2. YAML 隔离:敏感配置在 agent.yml 中,YAML 文件不提交到代码仓库
3. 运行时替换: ${OPENAI_API_KEY} 在运行时被环境变量值替换

```text
  1 # agent.yml 配置示例provider:api_key: ${OPENAI_API_KEY}

```

> **面试官想听的点：** 安全意识、环境隔离、配置分离

> **常见踩坑：** 说"先把 Key 写死在代码里,后面再改"——这是安全大忌。

## 类别五:模型   / 算法相关

### Q18. Embedding 模型如何选择?

**参考答案：** Embedding 模型选择取决于场景:

本项目默认使用 384 维 embedding( get_document_embedding_model 返回模型 dim_size=384),兼顾检索质量和存储开销。对于中文文档,考 虑切换到 bge-large-zh。

> **面试官想听的点：** 模型选型依据、中英文差异、成本意识

> **常见踩坑：** 说"用最大的模型"——没有免费的午餐,要考虑成本。

### Q19. 如何解决 RAG 的幻觉问题?

**参考答案：** RAG 幻觉指检索结果不相关或生成答案与检索内容不符。本项目的解决思路:

1. 检索层:混合检索(向量 + BM25)+ 多字段加权 + 多样性约束,提升召回质量
2. 生成层:Prompt 约束"只基于检索结果生成,不要自行编造"
3. 验证层:SQL 生成后通过执行验证结果合理性(空结果、异常值检测)

```text
  1 if result.is_empty:
  2  sql_state.warning = "Query returned no results"elif result.has_nulls:
  3  sql_state.warning = "Result contains null values"

```

> **面试官想听的点：** 幻觉来源理解、多层防护、验证兜底

> **常见踩坑：** 说"RAG 不会有幻觉"——这是错误的,幻觉来源是检索和生成两端。

### Q20. Rerank 是怎么做的?

**参考答案：** 本项目的 Rerank 是轻量级的多字段加权,而非 Cross-Encoder 二次排序:

```text
  1 final_score = (
  2  0.5 * vector_score # 向量相似度
  3  + 0.3 * text_score # BM25 得分
  4  + 0.1 * title_boost # 标题命中
  5  + 0.05 * hierarchy_boost # 层级命中
  6  + 0.05 * keywords_boost # 关键词命中
  7 )

```

轻量级 Rerank 的优势:不需要额外调用 LLM 或模型,延迟低;缺点:不如 Cross-Encoder 精确。如果需要更高精度,可引入 datus-storage-base 的 cross-encoder 功能。

> **面试官想听的点：** Rerank 原理、权重设计、轻量级 vs 重型方案

> **常见踩坑：** 说"Rerank 就是把结果再排一遍"——没有讲清楚加权公式和设计依据。

### Q21. Chunking 策略是怎样的?

**参考答案：** 文档分块(Chunking)在 SemanticChunker 中实现,基于文档结构(标题层级、段落)的语义分块,而非固定大小切分:

1. 层级拆分: max_heading_depth=3 限制,h4 以下内容扁平化到父节点
2. 段落优先:尽量保持完整段落,避免跨段落切分
3. 重叠保留: chunk_overlap=128 在块边界保留重叠内容,避免信息丢失
4. 小型合并:小于 min_chunk_size=256 的块会合并到相邻块

```text
  1 # 语义分块核心逻辑if section.level >= self.config.max_heading_depth:
  2  flat_text = self._flatten_section_content(section)
  3  return self._split_content(flat_text, ...)

```

> **面试官想听的点：** chunking 策略选择、语义完整性和召回率的平衡

> **常见踩坑：** 说"用固定大小切分就行"——这会破坏语义完整性。

### Q22. 评估指标有哪些?

**参考答案：** 本项目的评估指标体系:

1. 检索质量:F1(Precision + Recall)、NDCG
2. 生成质量:SQL 语法正确率、执行成功率
3. 性能指标:检索延迟、端到端响应时间
4. Benchmark:BIRD dataset、Spider 2.0-Snow

```text
  1 # 检索 F1 计算
  2 precision = relevant_retrieved / retrieved
  3 recall = relevant_retrieved / relevant
  4 f1 = 2 * precision * recall / (precision + recall)

```

Benchmark 结果在 benchmark 目录下,展示了不同配置下的准确率对比。

> **面试官想听的点：** 评估体系完整、指标可量化、Benchmark 意识

> **常见踩坑：** 说"我们靠用户反馈"——没有系统化的评估体系。

## 类别六:综合题

### Q23. 如果让你重新设计这个项目,你会怎么改?

**参考答案：** 如果重新设计,我会考虑:

1. 存储层分离:当前 Schema 元数据和 DocumentStore 耦合过紧,应该统一抽象为 RetrievalStore 接口,支持切换不同的向量后端(Milvus、 Pinecone)

2. 反思机制独立:当前反思和生成在同一节点,可以拆分为独立的  ReflectAgent ,支持配置不同的反思策略
3. 评估内置:benchmark 和评估框架应该在 CI 中自动运行,而不是手动触发
4. 流式输出:当前结果是整体返回,可以改造为流式输出,用户体验会更好

> **面试官想听的点：** 主动思考、发现问题、有改进思路

> **常见踩坑：** 说"不需要改"——说明没有深入思考项目局限。

### Q24. 这个项目如何部署到生产环境?

**参考答案：** 生产环境推荐 Docker Compose 部署:

1. 核心服务: datus-api REST API 服务,水平扩展
### 2. MCP 服务: datus-mcp MCP Server,独立进程

3. 向量库:LanceDB 嵌入式,无需单独部署
4. 会话存储: ~/.datus/sessions/ 映射到持久化存储

```text
  1 # docker-compose 片段services:datus-api:image: datus/datus-agentvolumes:- ./data:/root/.datusenv

```

监控方面,可接入 Prometheus + Grafana,关键指标:API QPS、检索延迟、SQL 生成成功率。

> **面试官想听的点：** 生产部署意识、Docker 使用、监控方案

> **常见踩坑：** 说"直接跑在服务器上"——没有容器化意识。

### Q25. 项目最大的技术难点是什么?

**参考答案：** 最大的难点是SQL 生成质量的稳定性。表面上是技术问题(检索、反思),实际上核心是:

1. 语义理解的边界:用户表达模糊时(如"按月统计"可能指日历月或财月),LLM 可能理解错误
2. Schema 覆盖的不完整性:表结构信息可能不包含业务含义(如某列存的是 status_code 但描述是"状态")
3. 反思的有限性:反思只能修复常见错误,复杂逻辑错误无法自动发现

我的应对策略:1)通过 few-shot learning 提供更多参考 SQL;2)Schema 描述尽量完整;3)预留 HITL 作为兜底。不追求 100% 自动解决,追求 80% 场景下用户零人工介入。

> **面试官想听的点：** 诚实面对局限、解决问题思路、期望管理

> **常见踩坑：** 说"没有难点"——这是不现实的。

## Data_engineer - 技术面总结

## 项目基础问题

### 介绍一下这个项目?

Data_engineer 是一个数据工程智能体,通过自然语言处理和语义搜索,将自然语言查询转换为准确的 SQL。核心是基于工作流节点编排的系统,把 SQL 生成分解为意图分类、Schema 链接、上下文检索、LLM 生成、执行验证等阶段,每个阶段由专门节点处理,通过有向无环图实现灵活编排。

### 这个项目是否涉及到harness?

是的,这个项目深度体现了 agent 设计的 harness 技术架构。 Data_engineer 的核心设计不是让 LLM 作为一个黑盒自由决策,而是将 LLM "装进"一套严格的结构化框架(即

harness/外骨骼)中进行可控执行。这套 harness 体现在以下层面:
1. Workflow + Node 双层抽象:Node 抽象基类定义了统一的执行接口(execute / setup_input / update_context),每种 LLM调用(Schema Linking、SQL 生成、执行、反思等)被封装为特定类型的节点,通过 workflow.yml 声明的 Plan 模板(如reflection、chat_agentic、 gensql_agentic 等)编排成 DAG 拓扑序执行,而非让 LLM 自行决定下一步做什么。
2. AgenticNode 作为强化 harness:继承自 Node 的 AgenticNode 为每个节点注入了 session 管理(AdvancedSQLiteSession)、tool集成(func tools + MCP servers)、权限管控(PermissionManager 三级 allow/deny/ask)、技能系统(SkillManager + SkillFuncTool)、Action 历史追踪 (ActionHistoryManager)、自动上下文压缩(auto-compaction at 90% token usage)以及streaming 执行支持,这些全部内嵌在 harness 层 面,节点实现者无需关心。

3. WorkflowRunner 作为 harness 的执行引擎:WorkflowRunner 负责工作流的生命周期管理(初始化、节点推进、evaluate_result质量评估、失败处理、轨迹持久化),按 node_order 顺序推进而非让 LLM 自由跳转,确保执行路径可预测、可审计、可复现。
4. 配置驱动的声明式 harness:通过 agent.yml 声明式配置 provider、节点模型、工具权限、技能模式等,Agent的运行时行为完全由外部 YAML 配置决定,LLM 本身不具备突破 harness 约束的能力。 简而言之,这个项目的 harness 范式就是:LLM 被"拴"在一套由 Node → Workflow → WorkflowRunner → Agent四级结构组成的受控管道中,每一步 执行都受到输入/输出类型约束、权限校验、质量评估和状态追踪的严格治理,而非让 LLM 作为自主Agent 自由决策。

### 这个项目和同类项目有什么区别?

在 Data_engineer 中,语义分块器(SemanticChunker)基于文档结构(标题层级、段落)做智能分块,保留完整的语义单元,同时通过 overlap 避免 边界信息丢失。

## 核心技术问题

## RAG 相关

### Q: 什么是 RAG?为什么它比直接让模型回答更适合企业知识问答?

RAG(检索增强生成)通过从企业知识库检索相关文档作为上下文,让 LLM 基于真实数据生成答案。相比直接让 LLM 回答,RAG 的优势在于:答案基 于实际检索到的内容而非模型记忆,因此不会产生幻觉;企业知识随时更新,RAG 能及时反映最新信息;每个答案可附带引用来源,方便用户核实。

### Q: RAG 和微调有什么区别?什么时候用哪个?

RAG 改变的是推理时输入的上下文,不改变模型本身;微调是通过训练改变模型的权重。RAG 适合知识会频繁更新、需要引用来源、多个知识领域共 存的场景;微调适合需要模型学习特定格式、语气或领域专有推理方式的场景。

### Q: 为什么说 chunking 决定了检索系统的上限?

Chunk太小会丢失上下文导致答案碎片化,chunk太大引入过多无关内容增加噪音。在 Data_engineer 中,语义分块器(SemanticChunker)基于文档 结构(标题层级、段落)做智能分块,保留完整的语义单元,同时通过 overlap 避免边界信息丢失。

### Q: embedding 模型怎么选?

中文场景用 bge-large-zh(开源免费,中文效果最佳);通用场景用 text-embedding-3-small 性价比最高;高精度需求用 text-embedding-3-large。

### Q: 为什么很多系统要加 rerank?

向量检索基于近似最近邻(ANN),追求速度但精度有限。Cross-Encoder 用完整 Transformer 对 query 和 doc 做精确相关性评分作为二次排序,能 显著提升检索质量。Data_engineer 中通过多字段加权(title、hierarchy、keywords)和多样性约束实现轻量级 rerank。

### Q: Hybrid Retrieval 的本质是什么?

同时使用多种检索方法(向量检索 + 关键词检索),各自取 Top 结果后加权融合。向量检索擅长语义理解,关键词检索擅长精确匹配。Data_engineer 的 OptimizedRecall 类实现了 BM25 + 向量的混合检索,通过可配置的权重组合两种信号。

## Agent 相关

### Q: 什么是 Agent?跟传统的 Chain 有什么区别?

Agent 是具有自主决策能力的 AI 程序,包含 LLM 核心、规划能力、记忆和工具使用四个组件。Chain 执行预定义的固定流程,Agent 根据中间结果动 态决定下一步,更灵活但也更难调试。Data_engineer 使用工作流节点图

### Q: 多 Agent 系统的编排模式有哪些?各自优缺点?

Data_engineer 采用 Pipeline + 条件分支的混合模式,通过 Workflow 管理节点执行顺序, SelectionNode 做意图分类实现条件路由。

### Q: 如何解决多 Agent 间的循环依赖和无限循环?

设置最大迭代次数(reflection_round 限制)、超时控制、Token 预算限制。 GenSQLAgenticNode 的反思机制最多重试 3 次,超过后触发人工介入 (HITLNode)。

### Q: 你的 Agent 系统如何保证容错性?

1. 各节点独立执行,单节点失败不影响其他节点
### 2. SQL 执行有超时保护(30s)和异常捕获

3. 反思机制自动修复常见错误
4. 降级策略:验证失败时提供备选方案

## GraphRAG 相关

### Q: 知识图谱在 RAG 中起什么作用?

纯向量检索只能捕获语义相似性,无法理解实体间的结构化关系。知识图谱保留实体间的显式关系(who → works_at → where),支持多跳推理:本 项目的 Schema 元数据存储了表间关系,支持跨表 JOIN 路径推理。

### Q: 子图检索的 Cypher 查询怎么写?

```text
  1 MATCH path = (start:Table {name: $table})-[*1..2]-(neighbor)
  2 RETURN start.name, type(relationship), neighbor.name
  3 LIMIT 50

```

可变长度路径匹配 [*1..2] 实现多跳遍历,本项目的 Schema Linking 通过类似思路发现间接相关的表。

## 框架对比相关

### Q: LangGraph vs CrewAI vs AutoGen 怎么选?

本项目专注于数据工程场景,内置 SQL 生成、Schema 链接、执行验证,无需从头开发。

### Q: 为什么选这个框架而不是直接调用?

1. 内置工作流编排,不需要手动管理状态传递
2. 节点可复用,不同查询可共用 Schema 链接、反思等节点
3. 支持 Plan 模式,复杂查询可先预览再执行
4. 内置 MCP 协议支持,开箱即用的 IDE 集成

## 系统设计相关

### Q: 系统的性能瓶颈在哪里?怎么优化?

向量索引已通过 create_vector_index() 创建 IVF_PQ 索引;LLM 生成可通过结果缓存复用相同查询的 SQL。

### Q: 如果文档规模扩大到 100 万,系统怎么扩展?

1. 向量库:从 LanceDB 单机迁移到 Milvus 集群(支持百亿级向量)
2. 文档解析:多 Worker 并行处理,Celery 任务队列
3. API 层:水平扩展,Kubernetes 多副本
4. 缓存:引入 Redis 缓存热点查询结果

综合开放问题

被质疑只是复现跑了一下项目,怎么回答?

这个项目我参与了核心检索模块的设计和实现。具体来说:1)我设计了混合检索策略,将 BM25 与向量检索结合,通过可配置的权重机制实现准确率 提升;2)我实现了语义分块器,基于文档结构做智能分块,而不是简单的固定大小切分;3)我优化了 Schema 链接流程,通过预计算索引将检索延迟 从秒级降到毫秒级。这些改进都在 benchmark 上有量化指标支撑。

这个项目有部署上线吗? 是的,项目已在公司内部部署使用。主要部署模式:1)CLI 模式供数据工程师日常使用;2)API 模式集成到内部数据平台;3)MCP 模式提供给 Claude Desktop 用户使用。生产环境使用 Docker Compose 部署,包含 API 服务、MCP 服务和 LanceDB 向量库。

测完接口性能后,你思考过如何优化吗? 有几个优化方向:1)结果缓存,对相同查询直接返回缓存的 SQL;2)批量预热,闲时预加载热点 Schema 到内存;3)模型蒸馏,用大模型生成的 SQL 作为伪标签,训练小模型做快速生成;4)索引优化,根据查询分布动态调整 IVF 索引的分区数。

Data_engineer — 技术面试「八股文」知识库

面向 AI/数据工程师岗位的系统化复习材料。可与本仓库 datus/ 目录实现对照阅读。每个主题含:概念辨析、适用场景、与本项目联系、简短代码或 伪代码、常见面试追问。

### 1. Agent vs Workflow vs Multi-Agent

Agent:具有自主决策能力的 AI 程序,核心组件包含 LLM 思维引擎、规划能力、记忆系统、工具调用。Agent 根据中间结果动态决定下一步,而非按 预设流程执行。 Workflow:预先定义好执行顺序的节点图(Pipeline / DAG),节点间有明确的依赖关系,执行顺序固定。本项目的 Workflow 即此模式。 Multi-Agent:多个专业 Agent 协作,各 Agent 职责单一,通过消息传递或共享状态协作。本项目采用单主 Agent + 多专业节点的模式

三者对比:Agent 适合开放性任务(需要动态决策),Workflow 适合确定性任务(路径已知),Multi-Agent 适合复杂任务的职责拆分。 本项目: Agent 类负责任务编排, Workflow 管理节点执行顺序, Node 是执行单元。 GenSQLAgenticNode 内部包含 LLM 驱动的反思决策,是 Agent 模式的体现。

```text
  1 # 本项目 Workflow 的执行模式(伪代码)class Workflow:
  2  def run(self):
  3    for node_id in self.node_order:
  4     node = self.nodes[node_id]
  5     state = node.execute(state) # 固定顺序执行

```

面试追问:「为什么不用纯 Agent 模式?」——因为 SQL 生成流程的大部分步骤是确定的(Schema 链接、执行验证),用 Workflow 可以减少 LLM 调用次数,降低成本和延迟。

### 2. Pipeline / DAG / 状态机

Pipeline:线性流水线,上游输出直接流入下游,适合各阶段输出独立的场景。 DAG(有向无环图):允许并行分支和条件路由,但不允许环。本项目的 Workflow 即 DAG——节点间有依赖但不构成环。 状态机:通过状态转移规则驱动,状态变更触发下一步行动。适合状态驱动的工作流。 本项目: Workflow 实现为 DAG,通过 node_order 确定拓扑序。 SelectionNode 的意图分类结果决定后续分支,实现条件路由。

```text
  1 # DAG 拓扑排序(伪代码)# 本项目的 Workflow 按 add_node 顺序决定 node_order
  2 workflow.add_node(BeginNode(), position=0)
  3 workflow.add_node(SchemaLinkingNode(), position=1)
  4 workflow.add_node(GenSQLAgenticNode(), position=2)
  5 # node_order = [BeginNode, SchemaLinkingNode, GenSQLAgenticNode]

```

### 3. ReAct / CoT / Reflection

ReAct(Reasoning + Acting):交替进行推理和动作执行,边想边做,适合需要外部工具调用的场景。

CoT(Chain of Thought):让模型逐步推理,输出推理链,适用于数学和逻辑问题。 Reflection:对生成结果进行自我反思,发现错误并修正。本项目的 ReflectNode + FixNode 即此模式。 本项目: GenSQLAgenticNode 先用 CoT 方式理解查询意图,再用 Reflection 验证生成的 SQL 是否正确、逻辑是否合理。

```text
  1 # 反思机制(伪代码)if not self._verify_sql(generated_sql):
  2  state.reflection_needed = True
  3  error = self._analyze_error(generated_sql)
  4  # FixNode 修复后重新验证

```

面试追问:「反思次数如何确定?」——本项目限制最多  3 次反射轮次,防止无限循环。

### 4. Tool Calling / Function Calling

Tool Calling:让 LLM 生成结构化的工具调用指令(如 JSON),而非自然语言。Function Calling 是 OpenAI 的实现版本。

本项目:通过 FuncTool 抽象将 Python 函数暴露给 LLM。 trans_to_function_tool 装饰器将函数签名转换为 LLM 可调用的工具定义。

```text
  1 class FuncToolResult:
  2  success: int # 1=成功, 0=失败
  3  result: Any # 返回数据
  4  error: str # 错误信息

```

面试追问:「Tool Calling 的局限是什么?」——工具参数需要精确的 JSON Schema,LLM 可能会生成参数格式错误或调用不存在的工具。

### 5. MCP(Model Context Protocol)

MCP:Anthropic 提出的标准协议,让 AI Agent 标准化地调用外部工具和服务。MCP Server 暴露工具,MCP Client 消费。

本项目:既实现了 MCP Server(通过 datus-mcp 暴露工具给 Claude Desktop、Cursor 等 IDE),也是 MCP Client(通过 .mcp 配置消费外部工具)。

```text
  1 # MCP Server 注册工具(伪代码)class MCPServer:
  2  def register_tool(self, tool: Tool):
  3    self.tools[tool.name] = tool

```

```text
  5  def handle_request(self, request):
  6    tool = self.tools[request.tool_name]
  7    return tool.execute(request.params)

```

### 6. 向量数据库与  Embedding

向量数据库:存储高维向量(embedding),通过 ANN(近似最近邻)算法实现语义相似度检索。代表产品:LanceDB、Milvus、Pinecone。 Embedding:将文本/图片等转换为高维向量的模型。维度越高信息越丰富,但检索成本越高。

本项目:使用 LanceDB 存储向量,通过 get_document_embedding_model 获取 embedding 模型,维度默认 384。 DocumentStore 的 search_docs 方法执行向量检索。

```text
  1 # 向量检索(伪代码)
  2 query_vector = embedding_model.embed(query)
  3 results = table.search_vector(
  4  query_vector,
  5  top_k=top_n,
  6  where=version_filter
  7 )

```

面试追问:「向量检索的精度瓶颈在哪?」——ANN 算法追求速度牺牲精度,对于语义模糊或跨领域的查询可能召回不相关结果。

### 7. RAG 与 Agent 的结合

RAG(Retrieval Augmented Generation):在 LLM 生成答案前,先检索相关文档作为上下文,解决 LLM 知识过时和幻觉问题。 RAG + Agent:Agent 在执行过程中调用 RAG 检索外部知识,检索结果作为 Prompt 上下文。本项目即此模式—— GenSQLAgenticNode 在生成 SQL 前先通过 DocumentStore 检索相关文档和参考 SQL。

```text
  1 # RAG 检索作为上下文(伪代码)
  2 docs = doc_store.search_docs(query=nl_query, top_k=5)
  3 ref_sqls = ref_sql_store.search_reference_sql(query=nl_query, top_k=3)

```

```text
  5 prompt = f"参考文档: {docs}\n参考SQL: {ref_sqls}\n问题: {nl_query}"

```

面试追问:「RAG 的检索质量如何优化?」——可从 chunking 策略(语义分块)、embedding 模型选择(中文 bge)、rerank(多字段加权)、 query expansion(扩展同义词)几个方向优化。

### 8. 并行执行与状态合并

并行执行:多个任务同时执行,提高吞吐量。本项目 StreamingDocProcessor 使用 ThreadPoolExecutor 并行处理多个文档。 状态合并:并行分支执行完毕后,需要合并各分支的结果。本项目在 SchemaLinkingNode 中并发检索多个表的 Schema,合并到 target_tables 。

```text
  1 # 并行检索 + 结果合并with ThreadPoolExecutor(max_workers=4) as executor:
  2  futures = [executor.submit(search_table, t) for t in tables]
  3  results = [f.result() for f in futures]
  4 merged = {r.table_name: r for r in results}

```

面试追问:「并行执行的状态冲突如何解决?」——通过读锁/写锁保护共享状态,或使用不可变数据结构(如返回新对象而非修改)。

### 9. 循环的终止条件设计

终止条件:防止 Agent / Workflow 进入无限循环,需要明确的退出条件。 本项目:Workflow 设置 reflection_round 限制反思次数, execute_sql_node.py 设置 30 秒执行超时。

```text
  1 # 终止条件(伪代码)if state.reflection_round >= 3:
  2  state.status = "max_reflection_reached"return state # 跳出循环,触发 HITLNodeif execution_time >
  3  state.error = "timeout"return state # 终止执行

```

面试追问:「如果 Agent 进入死循环怎么检测?」——设置最大迭代次数、Token 预算上限、执行超时,三重保护。

### 10. 熔断与降级策略

熔断:当外部服务失败率超过阈值时,快速失败(熔断)避免资源耗尽,而不是重试到超时。 降级:当服务不可用时,返回降级结果(如静态数据、缓存结果)而不是直接报错。 本项目:MCP 工具注册使用降级策略——当工具不可用时( has_xxx_tools = False ),工具列表中就不出现该工具,而不是抛出错误。

```text
  1 # 降级策略示例if self.has_metrics:
  2  tools.append(trans_to_function_tool(self.search_metrics))
  3 # 不抛异常,只是跳过不可用的工具

```

### 11. 缓存策略

缓存:避免重复计算和重复 API 调用,提升响应速度、降低成本。 本项目:使用多级缓存——Embedding 模型使用 lru_cache 缓存结果( get_document_embedding_model ),DocumentStore 使用 lru_cache 缓 存实例( document_store.cache_clear() )。

```text
  1 @lru_cache(maxsize=8)def document_store(platform: str) -> DocumentStore:
  2  """每个平台返回独立缓存的实例"""return DocumentStore(...)

```

面试追问:「缓存一致性问题如何处理?」——本项目使用删除后重新写入(delete-then-add)而非 merge_insert,避免写入冲突。

### 12. 知识增强 — BM25 与向量检索混合

BM25:基于词频的经典检索算法(类似 TF-IDF),精确匹配关键词时效果优于向量检索。

向量检索:基于语义相似度,适合同义词和语义扩展。 混合检索:同时使用两种方法,按权重融合结果。本项目的 OptimizedRecall 类实现此策略。

```text
  1 # 混合检索(伪代码)
  2 bm25_score = bm25.score(query, doc_index)
  3 vector_score = 1.0 / (rank + 1) # 从排名推导
  4 final_score = 0.5 * vector_score + 0.3 * bm25_score + 0.2 * field_boost

```

面试追问:「混合检索的权重如何确定?」——可以通过  grid search 在测试集上寻优,或根据线上用户点击数据动态调整。

### 13. SQL 执行验证与反思

SQL 验证:语法检查(SQLGlot)、执行验证(实际执行)、逻辑验证(结果合理性)。 反思:验证失败后,分析错误原因并尝试修复。本项目的 ReflectNode 分析错误, FixNode 尝试修复。

```text
  1 # 反思 + 修复流程(伪代码)
  2 is_valid = self._verify_syntax(sql)
  3 if not is_valid:
  4  error = self._analyze_error(sql) # 分析错误类型
  5  new_sql = self._fix_sql(sql, error) # 生成修复后的 SQLif self._verify_syntax(new_sql):
  6    state.generated_sql = new_sql

```

面试追问:「如果反思 3 次都失败了怎么办?」——触发 HITLNode(Human-In-The-Loop),将问题转给人工处理。

### 14. 可观测性 — 日志与  Trace

日志:结构化日志记录关键事件(INFO/WARNING/ERROR),方便排查问题。

Trace:请求级别的调用链追踪,串联一个请求在多个模块间的执行路径。 本项目:使用统一的 get_logger(name) 记录日志, optional_traceable 装饰器支持链路追踪。

```text
  1 logger = get_logger(__name__)
  2 logger.info(f"Processed {stats.total_docs} docs, {stats.total_chunks} chunks")
  3 logger.warning(f"Error processing {url}: {e}")

```

面试追问:「日志级别如何选择?」——DEBUG(开发调试)、INFO(正常流程关键节点)、WARNING(非致命问题)、ERROR(需要关注的问 题)。

### 15. Schema 链接与元数据检索

Schema 链接:将自然语言查询中的实体映射到数据库表结构(表名、列名、关系)。 本项目: SchemaLinkingNode 通过 SchemaWithValueRAG 检索相关表结构,使用向量相似度匹配查询与表/列描述。

```text
  1 # Schema 检索(伪代码)
  2 schema_results = schema_store.search_schema(
  3  query=nl_query, # 自然语言查询
  4  datasource=datasource,
  5  top_k=20, # 最多返回 20 个相关表
  6 )

```

面试追问:「Schema 链接错了怎么办?」—— ReflectNode 会验证生成的 SQL 中引用的表和列是否在 target_tables 中,如果发现错误会触发反思 修复。
