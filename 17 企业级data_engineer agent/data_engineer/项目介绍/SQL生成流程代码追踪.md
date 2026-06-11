# SQL 生成流程 代码追踪

## 概述

SQL 生成流程是本项目的核心机制，将用户自然语言查询转换为可执行的 SQL 语句。

**核心机制**：基于多节点工作流编排，通过 Schema 链接确定表结构，Agentic Node 生成 SQL，最后执行验证。

**涉及的节点**（串行执行）：
1. `BeginNode` → 初始化任务
2. `SelectionNode` → 意图分类
3. `SchemaLinkingNode` → 表结构检索
4. `GenSQLAgenticNode` → SQL 生成 + 反思
5. `ExecuteSQLNode` → 执行验证
6. `OutputNode` → 结果输出

---

## 调用链路

```
Agent.run()
  │
  └→ WorkflowRunner.run()
        │
        └→ for node_id in workflow.node_order:
              │
              ├→ BeginNode.execute()
              │     └→ state = SqlTaskState(...)
              │
              ├→ SelectionNode.execute()
              │     └→ classify_intent(nl_query)
              │
              ├→ SchemaLinkingNode.execute()
              │     └→ schema_store.search_schema()
              │
              ├→ GenSQLAgenticNode.execute()
              │     ├→ retrieve_context()
              │     ├→ llm.generate_sql()
              │     └→ verify_and_reflect()
              │
              ├→ ExecuteSQLNode.execute()
              │     └→ db_manager.execute()
              │
              └→ OutputNode.execute()
                    └→ format_output()
```

---

## BeginNode

### 调用链路

```
data_engineer/agent/node/begin_node.py:12
```

### 关键代码

```python
# data_engineer/agent/node/begin_node.py:14-30
class BeginNode(Node):
    async def execute(self, state: dict) -> dict:
        """初始化 SqlTaskState"""
        sql_state = SqlTaskState(
            task_id=self.task.task_id,
            nl_query=self.task.nl_query,
            datasource=self.task.datasource,
            session_id=self.task.session_id,
        )
        return {"sql_state": sql_state, **state}
```

---

## SelectionNode

### 调用链路

```
data_engineer/agent/node/selection_node.py:25
```

### 关键代码

```python
# data_engineer/agent/node/selection_node.py:26-45
async def execute(self, state: dict) -> dict:
    """根据查询内容分类意图"""
    nl_query = state["sql_state"].nl_query

    # 意图分类逻辑
    if contains_metric_keywords(nl_query):
        intent = "metrics"
    elif contains_sql_keywords(nl_query):
        intent = "sql_generation"
    else:
        intent = "general"

    state["intent"] = intent
    return state
```

---

## SchemaLinkingNode

### 调用链路

```
data_engineer/agent/node/schema_linking_node.py:35
  └→ data_engineer/storage/schema_metadata/store.py:search_schema()
```

### 关键代码

```python
# data_engineer/agent/node/schema_linking_node.py:36-60
class SchemaLinkingNode(Node):
    async def execute(self, state: dict) -> dict:
        sql_state = state["sql_state"]

        # 检索相关表结构
        schema_results = self.schema_store.search_schema(
            query=sql_state.nl_query,
            datasource=sql_state.datasource,
            top_k=20,
        )

        # 筛选相关表和字段
        relevant_tables = filter_relevant_tables(
            schema_results,
            sql_state.nl_query,
        )

        sql_state.target_tables = relevant_tables
        state["sql_state"] = sql_state
        return state
```

```python
# data_engineer/storage/schema_metadata/store.py:55-80
class SchemaWithValueRAG:
    def search_schema(self, query: str, top_k: int = 20) -> List[Dict]:
        """向量搜索相关表结构"""
        # 1. 将查询嵌入为向量
        query_vector = self.embedding_model.embed(query)

        # 2. LanceDB 向量检索
        results = self.table.search_vector(
            query_vector,
            top_k=top_k,
        )

        # 3. 解析结果
        return [parse_row(row) for row in results]
```

---

## GenSQLAgenticNode

### 调用链路

```
data_engineer/agent/node/gen_sql_agentic_node.py:45
  ├→ _run_once()
  │     ├→ _build_prompt()
  │     ├→ _retrieve_context()
  │     ├→ _call_llm()
  │     └→ _verify_sql()
  │
  └→ data_engineer/tools/func_tool/context_search.py:search_context()
```

### 核心代码片段

```python
# data_engineer/agent/node/gen_sql_agentic_node.py:46-120
async def _run_once(self, state: SqlTaskState) -> SqlTaskState:
    """单次执行：理解 → 检索 → 生成 → 验证"""

    # 1. 构建 Prompt
    prompt = self._build_prompt(state)

    # 2. 检索相关上下文
    context = await self._retrieve_context(state)

    # 3. 调用 LLM 生成 SQL
    response = await self._call_llm(
        prompt=prompt,
        context=context,
    )

    # 4. 解析生成的 SQL
    generated_sql = parse_sql_from_response(response)

    # 5. 验证 SQL 正确性
    is_valid, error = await self._verify_sql(generated_sql)

    if not is_valid:
        # 触发反思/修复流程
        state.reflection_needed = True
        state.error = error

    state.generated_sql = generated_sql
    return state
```

```python
# data_engineer/agent/node/gen_sql_agentic_node.py:121-145
def _build_prompt(self, state: SqlTaskState) -> str:
    """构建 SQL 生成 Prompt"""
    # 注入 Schema 信息
    schema_context = format_schema(state.target_tables)

    # 注入参考 SQL
    ref_sql = self._get_reference_sql(state)

    prompt = f"""
    给定以下数据库 Schema:
    {schema_context}

    参考 SQL 示例:
    {ref_sql}

    生成 SQL 来回答以下问题:
    {state.nl_query}

    只返回 SQL，不要其他解释。
    """
    return prompt
```

```python
# data_engineer/agent/node/gen_sql_agentic_node.py:146-175
async def _retrieve_context(self, state: SqlTaskState) -> Dict:
    """检索相关上下文：Schema、文档、指标"""
    context = {}

    # 检索相关文档
    docs = self.doc_store.search_docs(
        query=state.nl_query,
        top_k=5,
    )
    context["docs"] = docs

    # 检索参考 SQL
    ref_sqls = self.ref_sql_store.search_reference_sql(
        query=state.nl_query,
        top_k=3,
    )
    context["reference_sql"] = ref_sqls

    # 检索相关指标（如果需要）
    if state.intent == "metrics":
        metrics = self.metric_rag.search_metrics(
            query=state.nl_query,
        )
        context["metrics"] = metrics

    return context
```

---

## ExecuteSQLNode

### 调用链路

```
data_engineer/agent/node/execute_sql_node.py:30
  └→ data_engineer/tools/db_tools/db_manager.py:execute()
```

### 关键代码

```python
# data_engineer/agent/node/execute_sql_node.py:31-55
class ExecuteSQLNode(Node):
    async def execute(self, state: dict) -> dict:
        sql_state = state["sql_state"]
        sql = sql_state.generated_sql

        # 获取数据库连接
        connector = self.db_manager.get_connector(sql_state.datasource)

        try:
            # 执行 SQL
            result = await connector.execute(sql)

            # 验证结果
            if result.is_empty:
                sql_state.warning = "Query returned no results"
            else:
                sql_state.result = result

            sql_state.executed = True

        except SQLExecuteError as e:
            sql_state.execution_error = str(e)
            sql_state.executed = False

        return state
```

```python
# data_engineer/tools/db_tools/db_manager.py:80-110
class DBManager:
    def execute(self, sql: str, datasource: str) -> QueryResult:
        """执行 SQL 并返回结果"""
        connector = self._connectors[datasource]

        # 参数化查询防注入
        params = self._extract_params(sql)
        validated_sql = self._validate_sql(sql)

        return connector.execute(validated_sql, params)
```

---

## OutputNode

### 调用链路

```
data_engineer/agent/node/output_node.py:25
```

### 关键代码

```python
# data_engineer/agent/node/output_node.py:26-50
class OutputNode(Node):
    def execute(self, state: dict) -> dict:
        sql_state = state["sql_state"]

        # 格式化输出
        output = {
            "sql": sql_state.generated_sql,
            "executed": sql_state.executed,
            "result": format_result(sql_state.result),
            "tables_used": sql_state.target_tables,
            "execution_time": sql_state.execution_time,
        }

        # 输出到终端
        self._print_formatted(output)

        return state
```

---

## 错误恢复流程

### SQL 生成失败

```
GenSQLAgenticNode.execute()
  │
  ├→ [SQL 验证失败]
  │     │
  │     └→ state.reflection_needed = True
  │
  └→ workflow.next_node("reflect")
        │
        ├→ ReflectNode.execute()
        │     └→ 分析错误原因
        │
        └→ FixNode.execute()
              └→ 尝试修复 SQL
                    │
                    ├→ [修复成功] → ExecuteSQLNode
                    │
                    └→ [修复失败] → HITLNode (人工介入)
```

### 执行超时

```
ExecuteSQLNode.execute()
  │
  └→ [超时 30s]
        │
        ├→ 取消查询
        ├→ state.timeout = True
        │
        └→ 返回错误信息
              │
              └→ 提示用户优化查询条件
```

---

## 关键代码片段汇总

### 1. Schema 检索 (schema_linking_node.py:50)

```python
relevant_tables = self.schema_store.search_schema(
    query=state.nl_query,
    datasource=state.datasource,
    top_k=20,
)
```

### 2. Prompt 构建 (gen_sql_agentic_node.py:125)

```python
prompt = f"""
Schema: {schema_context}
Examples: {ref_sql}
Question: {state.nl_query}
SQL:
"""
```

### 3. LLM 调用 (gen_sql_agentic_node.py:160)

```python
response = await self.llm.agenerate(
    messages=[{"role": "user", "content": prompt}],
    model=self.config.model,
)
```

### 4. SQL 验证 (gen_sql_agentic_node.py:100)

```python
is_valid = self._validate_syntax(sql)
if not is_valid:
    error = self._analyze_error(sql)
```

### 5. SQL 执行 (execute_sql_node.py:40)

```python
result = await connector.execute(sql, timeout=30)
```

### 6. 结果格式化 (output_node.py:35)

```python
output = f"SQL: {sql}\nResult: {result.rows}"
```
