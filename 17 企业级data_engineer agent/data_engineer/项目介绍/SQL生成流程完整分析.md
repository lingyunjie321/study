# SQL 生成流程 完整分析

## 目录

- [概述](#概述)
- [读取/加载机制](#读取加载机制)
- [完整生命周期](#完整生命周期)
- [各节点详细步骤](#各节点详细步骤)
- [关键数据结构](#关键数据结构)
- [代码追踪](#代码追踪)
- [完整执行示例](#完整执行示例)
- [关键设计模式](#关键设计模式)
- [常见问题排查](#常见问题排查)

---

## 概述

SQL 生成流程是本数据工程智能体的核心能力，将用户的自然语言查询转换为可执行的 SQL 语句。

**一句话概括**：基于工作流节点编排的多阶段流程，通过意图分类 → Schema 链接 → 上下文检索 → LLM 生成 → 执行验证的流水线，将自然语言映射为准确的 SQL。

### 两种子流程对比

| 类型 | 说明 |
|------|------|
| 直接生成 | NL → 意图 → Schema → 生成 → 执行 → 输出（简单查询） |
| 反思修复 | NL → 意图 → Schema → 生成 → 验证失败 → 反思 → 修复 → 重新执行（复杂查询） |

---

## 读取/加载机制

### 1. Schema 元数据加载

```python
# 启动时加载所有表的 Schema 到内存
SchemaWithValueRAG.search_schema()
  └→ LanceDB 向量检索
        ├→ 表名 embedding
        ├→ 列名 embedding
        └→ 描述 embedding
```

**缓存策略**：
- Schema 信息缓存在 `SchemaWithValueRAG` 实例中
- 新表接入时重新加载

### 2. 上下文检索加载

| 上下文类型 | 加载方式 | 缓存 |
|-----------|---------|------|
| 参考 SQL | 向量检索 | Session 级 |
| 平台文档 | DocumentStore | 项目级 |
| 业务指标 | MetricRAG | 项目级 |

### 3. 配置来源

```python
# 配置优先级（高 → 低）
1. CLI 参数 --datasource
2. .data_engineer/config.yml
3. agent.yml 默认值
```

---

## 完整生命周期

### 流程图

```
用户输入: "查询每月营收 TOP 10 的产品"
│
├─[阶段1] 初始化
│  └─ BeginNode
│       ├─ 创建 SqlTaskState
│       ├─ 设置 task_id, session_id
│       └─ 输出: {task_id, nl_query, datasource}
│
├─[阶段2] 意图分类
│  └─ SelectionNode
│       ├─ 解析 nl_query 关键词
│       ├─ 判断: sql_generation / metrics / doc_search
│       └─ 输出: {intent: "sql_generation"}
│
├─[阶段3] Schema 链接
│  └─ SchemaLinkingNode
│       ├─ 向量检索相关表 (top_k=20)
│       ├─ 字段过滤
│       └─ 输出: {target_tables: [...]}
│
├─[阶段4] 上下文检索
│  └─ GenSQLAgenticNode._retrieve_context()
│       ├─ 检索参考 SQL (top_k=3)
│       ├─ 检索相关文档 (top_k=5)
│       └─ 输出: {docs, reference_sql}
│
├─[阶段5] SQL 生成
│  └─ GenSQLAgenticNode._call_llm()
│       ├─ 构建 Prompt (Schema + 上下文)
│       ├─ 调用 LLM
│       └─ 解析生成的 SQL
│
├─[阶段6] 验证反思
│  └─ GenSQLAgenticNode._verify_sql()
│       ├─ 语法检查
│       ├─ 逻辑验证
│       └─ [失败?] → 触发反思
│
├─[阶段7] 执行
│  └─ ExecuteSQLNode
│       ├─ 获取数据库连接
│       ├─ 执行 SQL (timeout=30s)
│       └─ 返回结果集
│
└─[阶段8] 输出
   └─ OutputNode
        ├─ 格式化结果
        └─ 输出到终端
```

---

## 各节点详细步骤

### 阶段 1: BeginNode

**输入**：SqlTask（包含 nl_query, datasource）

**处理**：
1. 创建 SqlTaskState 空状态
2. 填充任务基本信息
3. 设置初始 status="pending"

**输出**：SqlTaskState

---

### 阶段 2: SelectionNode

**输入**：SqlTaskState.nl_query

**处理**：
1. 提取查询中的关键词
2. 匹配意图规则：
   - 含 "收入"、"利润"、"KPI" → metrics
   - 含 "表"、"字段"、"schema" → schema_inquiry
   - 其他 → sql_generation

**输出**：SqlTaskState + intent

---

### 阶段 3: SchemaLinkingNode

**输入**：SqlTaskState + nl_query

**处理**：
1. 将 nl_query 嵌入为向量
2. 在 LanceDB 中检索 top_k=20 相关表
3. 解析每张表的列信息
4. 筛选相关列（去除明显无关表）

**输出**：SqlTaskState.target_tables

---

### 阶段 4: GenSQLAgenticNode

**输入**：SqlTaskState（包含 target_tables, nl_query）

**处理**：

#### 步骤 4.1: 上下文检索

```python
# 并发检索三种上下文
docs = doc_store.search_docs(query, top_k=5)
ref_sqls = ref_sql_store.search(query, top_k=3)
metrics = metric_rag.search(query)  # 如果是 metrics 意图
```

#### 步骤 4.2: Prompt 构建

```python
prompt = f"""
你是一个 SQL 专家。根据以下信息生成 SQL。

【数据库 Schema】
{tables}

【参考示例】
{ref_sqls}

【相关文档】
{docs}

【用户问题】
{nl_query}

请生成准确的 SQL。
"""
```

#### 步骤 4.3: LLM 调用

```python
response = await llm.agenerate(messages=[...])
sql = parse_sql(response)
```

**输出**：SqlTaskState.generated_sql

---

### 阶段 5: 验证反思

**输入**：generated_sql

**处理**：

| 检查项 | 方法 | 失败处理 |
|--------|------|---------|
| 语法正确 | SQLGlot 解析 | 修复语法 |
| 表存在 | Schema 校验 | 反馈用户 |
| 列存在 | Schema 校验 | 修复列名 |
| 逻辑合理 | LLM 反思 | 重新生成 |

**反思流程**：

```
[验证失败]
    │
    ├→ GenSQLAgenticNode._reflect()
    │     └→ 分析错误原因
    │
    ├→ FixNode 修复
    │     └→ 尝试修复 SQL
    │
    └→ [循环直到成功 or max_try]
```

---

### 阶段 6: 执行

**输入**：generated_sql, datasource

**处理**：
1. 获取数据库连接（连接池）
2. 参数化处理
3. 执行 SQL
4. 捕获异常

**输出**：QueryResult

---

### 阶段 7: 输出

**输入**：QueryResult

**处理**：
1. 格式化表格输出
2. 显示执行时间
3. 显示 SQL 语句

---

## 关键数据结构

### SqlTask

```python
@dataclass
class SqlTask:
    task_id: str              # 任务 ID，UUID 格式
    nl_query: str            # 自然语言查询
    datasource: str          # 数据源名称
    target_tables: List[str] = []  # 涉及的表
    session_id: str = ""     # 所属会话
```

### SqlTaskState

```python
@dataclass
class SqlTaskState:
    task_id: str
    nl_query: str
    datasource: str

    # 中间结果
    intent: str = ""
    target_tables: List[TableInfo] = []
    generated_sql: str = ""
    executed: bool = False
    result: Optional[QueryResult] = None

    # 错误处理
    error: Optional[str] = None
    reflection_needed: bool = False

    # 元数据
    created_at: str = ""
    updated_at: str = ""
```

### TableInfo

```python
@dataclass
class TableInfo:
    table_name: str           # 表名
    columns: List[ColumnInfo] # 列
    description: str = ""     # 表描述
    row_count: int = 0       # 行数（采样）
```

---

## 代码追踪

### 精简版调用链

```
Agent.run()
  └→ WorkflowRunner.run()
        └→ node.execute(state)
              │
              ├→ BeginNode: 初始化
              ├→ SelectionNode: 意图分类
              ├→ SchemaLinkingNode: Schema 链接
              ├→ GenSQLAgenticNode: 生成 + 反思
              ├→ ExecuteSQLNode: 执行
              └→ OutputNode: 输出
```

### 关键文件

| 文件 | 职责 |
|------|------|
| `agent.py:run()` | 主循环入口 |
| `workflow_runner.py:run()` | 节点执行调度 |
| `node/begin_node.py` | 状态初始化 |
| `node/selection_node.py` | 意图分类 |
| `node/schema_linking_node.py` | Schema 检索 |
| `node/gen_sql_agentic_node.py` | SQL 生成核心 |
| `node/execute_sql_node.py` | SQL 执行 |
| `node/output_node.py` | 结果输出 |

---

## 完整执行示例

### 输入

```
用户: "查询每月营收 TOP 10 的产品"
数据源: demo (DuckDB)
```

### 中间状态

| 阶段 | 输出 |
|------|------|
| Begin | task_id="abc123", nl_query="查询每月营收 TOP 10 的产品" |
| Selection | intent="sql_generation" |
| SchemaLink | target_tables=[products, orders, order_items] |
| GenSQL | generated_sql="SELECT ..." |
| Execute | result=QueryResult(rows=10) |
| Output | formatted_table |

### 最终输出

```
┌─ SQL ─────────────────────────────────────────┐
│ SELECT                                         │
│   p.name,                                      │
│   DATE_TRUNC('month', o.created_at) as month, │
│   SUM(o.total) as revenue                      │
│ FROM products p                                │
│ JOIN orders o ON p.id = o.product_id          │
│ GROUP BY p.name, DATE_TRUNC('month', ...)     │
│ ORDER BY revenue DESC                         │
│ LIMIT 10                                       │
└────────────────────────────────────────────────┘

执行时间: 0.23s
结果: 10 行
```

---

## 关键设计模式

### 1. 工作流编排模式 (Pipeline Pattern)

```
Workflow 管理节点执行顺序
     │
     ├→ 线性依赖: A → B → C → D
     ├→ 条件分支: if X then A else B
     └→ 并行执行: A || B || C
```

**优势**：解耦各阶段逻辑，方便独立测试和替换

### 2. 工厂模式 (Factory Pattern)

```python
# Node.new_instance() 根据 node_type 创建对应节点
Node.new_instance(
    node_id="gen_sql",
    node_type="gen_sql",
) → GenSQLAgenticNode
```

**优势**：新增节点类型无需修改调用方代码

### 3. 策略模式 (Strategy Pattern)

```python
# 不同数据库使用不同 SQL 验证策略
class SQLValidator:
    strategies = {
        "duckdb": DuckDBStrategy(),
        "postgresql": PostgreSQLStrategy(),
    }
```

**优势**：支持多数据库方言的差异化处理

### 4. 观察者模式 (Observer Pattern)

```python
# 工作流状态变更通知
workflow.add_observer(lambda state: save_to_history(state))
workflow.add_observer(lambda state: update_ui(state))
```

**优势**：状态变更触发多端同步

---

## 常见问题排查

### Q1: Schema 链接结果为空

**检查清单**：
1. [ ] 数据库是否已初始化 Schema？
2. [ ] 表名是否包含在嵌入数据中？
3. [ ] 查询关键词是否与表描述匹配？

```bash
# 验证 Schema 是否存在
data_engineer-cli --datasource demo /List tables
```

### Q2: LLM 生成 SQL 语法错误

**检查清单**：
1. [ ] Schema 信息是否正确传入？
2. [ ] Prompt 是否包含足够的上下文？
3. [ ] LLM 模型是否支持该数据库方言？

```python
# 启用详细日志
import logging
logging.getLogger("data_engineer").setLevel(logging.DEBUG)
```

### Q3: SQL 执行超时

**检查清单**：
1. [ ] 查询条件是否加了 LIMIT？
2. [ ] 是否缺少索引？
3. [ ] 数据量是否过大？

```python
# 设置执行超时
connector.execute(sql, timeout=30)
```

---

## 性能优化建议

### 已有的优化措施

1. **Schema 预加载**：启动时一次性加载，避免重复查询
2. **连接池**：复用数据库连接
3. **向量索引**：LanceDB IVF_PQ 索引加速检索

### 可进一步优化的方向

| 方向 | 当前方案 | 改进思路 |
|------|---------|---------|
| Prompt 压缩 | 完整 Schema | 按需裁剪 |
| 缓存复用 | Session 级 | 项目级缓存 |
| 并行检索 | 串行上下文 | 并发获取 |
| LLM 蒸馏 | GPT-4 | 本地小模型 |
