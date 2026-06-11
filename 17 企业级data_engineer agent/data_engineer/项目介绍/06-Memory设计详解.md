# Data Engineer Agent Memory 设计详解

## 概述

Data Engineer Agent 的 memory 设计不是传统的"短期记忆/长期记忆"二分法，而是一套**多层累积式上下文管理系统**，贯穿 SDK 层 → Workflow 层 → 反思层。整体架构如下：

```
┌──────────────────────────────────────────────────┐
│                  Prompt 层                        │
│  system prompt + memory_context + AGENTS.md       │
├──────────────────────────────────────────────────┤
│              SDK 层 (AdvancedSQLiteSession)        │
│  对话历史持久化 (SQLite) / 自动 compact           │
├──────────────────────────────────────────────────┤
│            Workflow 层 (Context)                   │
│  sql_contexts / schemas / metrics / docs          │
├──────────────────────────────────────────────────┤
│              反思层 (ReflectNode)                 │
│  StrategyType 策略决策 → workflow 动态调整         │
├──────────────────────────────────────────────────┤
│            存储层 (LanceDB + SQLite)               │
│  session/{session_id}.db / schema / metrics       │
└──────────────────────────────────────────────────┘
```

---

## 设计思路：两条轴，四层记忆

Data Engineer Agent 的 memory 不是传统 LLM 应用里一个集中的 Memory 模块，而是**沿两条轴分散到四个层次**的上下文管理体系。

### 时间轴：从秒级到永久

```
请求级（单次 LLM 调用）  →  system prompt 中的 memory_context 注入
   ↓
任务级（一次 SQL 生成）  →  workflow Context 累积 sql_contexts 链
   ↓
会话级（多轮对话）      →  AdvancedSQLiteSession 持久化 + 自动 compact
   ↓
项目级（跨会话）        →  LanceDB 知识库（schema / metrics / docs）
```

每往下一层，数据生命周期越长、检索方式越复杂、更新频率越低。

### 范围轴：从全局到局部

```
AGENTS.md         →  全局项目上下文，所有节点共享
memory 目录       →  按 node_name 隔离，chat 和 gen_sql 互不干扰
workflow Context  →  单次 workflow 内共享，不同 workflow 完全隔离
sub-agent session →  ephemeral 纯内存，用完即销毁
```

### 为什么分四层而不是一个统一 Memory 模块？

| 层 | 解决的问题 | 为什么不能合并 |
|----|----------|--------------|
| Prompt 层 | LLM 调用时"需要知道什么" | 注入逻辑和 prompt 构建强耦合，依赖模板渲染 |
| SDK 层 | 对话历史"存在哪里、怎么压缩" | 是 OpenAI Agents SDK 的能力边界，替换 SDK 要整体换掉 |
| Workflow 层 | 多步任务"中间结果怎么传递" | 生命周期和 workflow 强绑定，workflow 结束即销毁 |
| 反思层 | 结果出错"怎么修正" | 直接影响 workflow 结构，不只是记忆读写 |

每一层有自己的**生命周期、读写频率、存储后端**，分层后各自独立演进：换一个 session 存储方案不影响 Context 流转，改反思策略不影响对话持久化。

---

## 一、SDK 层：AdvancedSQLiteSession（对话持久化）

### 1.1 类与来源

`agentic_node.py:20` 导入了 OpenAI Agents SDK 内置的 session 机制：

```python
from agents.extensions.memory import AdvancedSQLiteSession
```

每个 `AgenticNode` 实例持有一个 `_session` 属性和 `session_id`，通过 `_get_or_create_session()` 懒初始化。

### 1.2 两种 Session 模式

`agentic_node.py:507-535`

| 模式 | 触发条件 | 存储方式 | 适用场景 |
|------|---------|---------|---------|
| **持久化模式** | 默认 (`ephemeral=False`) | `model.create_session(session_id)` → 写入磁盘 SQLite | Chat 节点、顶层交互 |
| **Ephemeral 模式** | `ephemeral=True` | `AdvancedSQLiteSession(db_path=":memory:")` → 纯内存 | Sub-agent（子代理），用完即丢 |

```python
def _get_or_create_session(self):
    if self._session is None:
        if self.session_id is None:
            self.session_id = self._generate_session_id()  # e.g. "chat_session_a1b2c3d4"

        if self.ephemeral:
            self._session = AdvancedSQLiteSession(
                session_id=self.session_id,
                db_path=":memory:",       # 不落盘
                create_tables=True,
            )
        else:
            self._session = self.model.create_session(self.session_id)  # 落盘
    return self._session, None
```

### 1.3 Session 存储路径

`CLAUDE.md:86`：

```
~/.data_engineer/sessions/{project_name}/{session_id}.db
```

项目名从 `os.getcwd()` 派生，按项目隔离。不同项目的 session 互不干扰。

### 1.4 自动 Compaction（对话压缩）

当 token 使用量逼近模型 context window 时，系统自动触发 compaction，将历史对话压缩为摘要写入 session。`agentic_node.py:244-258` 提供了 `context_length` 属性动态读取当前模型的 context window 大小，供 compaction 策略计算空间预算。

```python
@property
def context_length(self) -> Optional[int]:
    current = self.model
    if current is None:
        return None
    return current.context_length()
```

在 `ChatAgenticNode.execute_stream()` 的每次执行前会调用 `await self._auto_compact()` 检查是否需要压缩。

---

## 二、Prompt 层：Memory Context 注入

### 2.1 memory_enabled 开关

`agentic_node.py:101,152`：

每个 AgenticNode 都有 `memory_enabled` 属性，控制是否在 system prompt 中注入 memory 片段。

```python
self.memory_enabled: bool = (
    memory_enabled if memory_enabled is not None
    else has_memory(self.get_node_name())
)
```

默认规则（由 `data_engineer.utils.memory_loader.has_memory()` 决定）：

| 节点类型 | memory 默认 |
|---------|------------|
| `chat` | **开启** |
| 自定义/user-defined subagent | **开启** |
| `gen_sql` / `gen_report` / `feedback` 等内置 subagent | **关闭** |

> 内置 subagent 关闭 memory 是为了保持 prompt 聚焦于当前任务，不被历史上下文干扰。

### 2.2 _inject_memory_context 流程

`agentic_node.py:429-474`：

1. 如果是 feedback 等特殊节点，允许 `override_node_name` 参数注入**调用者**的 memory（而非自身的）
2. 从 `{workspace_root}/.data_engineer/memory/{node_name}/` 目录加载 memory 内容
3. 通过 `memory_context` prompt 模板渲染后追加到 system prompt 末尾

```python
def _inject_memory_context(self, base_prompt, override_node_name=None):
    # feedback 路径无条件注入调用者的 memory
    if override_node_name:
        node_name = override_node_name
    else:
        if not self.memory_enabled:
            return base_prompt         # 内置 subagent 默认跳过
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

### 2.3 AGENTS.md 项目上下文

`agentic_node.py:476-501`：

除了 per-node memory，系统还会读取 `{cwd}/AGENTS.md` 的前 200 行，作为 `<project_context>` 注入 system prompt。这提供了项目级的长效上下文。

### 2.4 System Prompt 最终组装顺序

`_finalize_system_prompt()` 的执行顺序：

1. Base prompt（模板渲染）
2. AGENTS.md 项目上下文
3. Skills XML（可用技能列表）
4. **Memory context**（节点级记忆）
5. Language directive（输出语言约束）

---

## 三、Workflow 层：Context（工作记忆）

### 3.1 Context 模型

`schemas/node_models.py:493-564`：

```python
class Context(BaseModel):
    sql_contexts: List[SQLContext]     # ← 核心：SQL 执行历史链
    table_schemas: List[TableSchema]   # Schema 缓存
    table_values: List[TableValue]     # 样本数据缓存
    metrics: List[Metric]              # 指标缓存
    doc_search_keywords: List[str]     # 文档检索关键词
    document_result: DocSearchResult   # 文档检索结果
    parallel_results: Dict             # 并行节点执行结果
    last_selected_result: Any          # Selection 节点的选择结果
    selection_metadata: Dict           # Selection 元数据
```

`Context` 属于 `Workflow` 实例（`workflow.py:51`），随 workflow 生命周期存在。它充当**一次 SQL 生成任务中的工作记忆**，各 Node 通过 `update_context()` / `setup_input()` 读写它。

### 3.2 SQLContext —— 每轮 SQL 的记忆单元

```python
class SQLContext(BaseModel):
    sql_query: str                          # 生成的 SQL
    explanation: str                        # SQL 解释
    sql_return: Any                         # 执行结果（DataFrame/CSV）
    sql_error: str                          # 执行错误
    row_count: int                          # 返回行数
    reflection_strategy: str                # 反思采用的策略
    reflection_explanation: str             # 反思解释
```

`Context.sql_contexts` 是一个 **List**，按时间顺序追加。每次 SQL 生成→执行→反思 会新增一个 `SQLContext`。后续的 `GenerateSQLNode` 会将所有历史 `sql_contexts` 拼入 prompt，实现**上下文延续和多轮修正**。

### 3.3 Context 在 Node 间的流转

```
┌──────────┐   setup_input()    ┌──────────┐
│  Node A  │ ──────────────────→ │  Node B  │
│ (完成)   │ ←────────────────── │ (当前)   │
└──────────┘   update_context() └──────────┘
      ↑                              │
      │    workflow.context           │
      └──────────────────────────────┘
```

- `setup_input(workflow)`: 从 `workflow.context` 读取上游结果，构造当前 Node 的 input
- `update_context(workflow)`: 将当前 Node 的 result 写回 `workflow.context`

例如 `ReflectNode.update_context()` 会将反思策略和解释写回最后一个 `SQLContext`：

```python
last_record = workflow.context.sql_contexts[-1]
last_record.reflection_strategy = strategy
last_record.reflection_explanation = result.details.get("explanation", "")
```

---

## 四、反思层：ReflectNode + StrategyType

### 4.1 反思策略枚举

`schemas/node_models.py:621-631`：

```python
class StrategyType(str, Enum):
    SUCCESS = "SUCCESS"                       # SQL 执行正确，直接输出
    DOC_SEARCH = "DOC_SEARCH"                 # 需要查文档
    SIMPLE_REGENERATE = "SIMPLE_REGENERATE"   # 简单重新生成
    SCHEMA_LINKING = "SCHEMA_LINKING"         # 重新做 Schema Linking
    REASONING = "REASONING"                   # 增强推理
    COLUMN_EXPLORATION = "COLUMN_EXPLORATION" # 探索列信息
    UNKNOWN = "UNKNOWN"                       # 无法判断
```

### 4.2 反思循环

`reflect_node.py:89-126`：

1. 每次 SQL 执行后，`ReflectNode` 调用 LLM 评估结果
2. 根据评估建议的策略，动态向 workflow 中插入新节点
3. 有最大反思轮次限制（环境变量 `MAX_REFLECTION_ROUNDS`，默认 3）

```
轮次 1: SIMPLE_REGENERATE → 直接在 workflow 当前位置插入 regenerate 节点
轮次 2: SCHEMA_LINKING    → 插入 schema_linking 节点重新匹配表
轮次 3: REASONING         → 达到上限，强制执行推理节点
轮次 4:                   → 超出上限，强制终止
```

```python
max_round = get_env_int("MAX_REFLECTION_ROUNDS", 3)
if workflow.reflection_round == max_round:
    return self._execute_strategy(details, workflow, StrategyType.REASONING)
elif workflow.reflection_round > max_round:
    return {"success": True, "message": "Max reflection rounds exceeded"}
```

### 4.3 策略执行：动态 Workflow 调整

`reflect_node.py:128-174`：

反思不是简单的"再试一次"，而是**动态向 workflow 插入新节点**：

```python
for node_type in reflection_nodes:
    new_node = Node.new_instance(
        node_id=f"reflect_{workflow.reflection_round}_{node_type}",
        node_type=node_type,
        ...
    )
    workflow.add_node(new_node, current_position + 1)
```

这种设计让反思不仅是一条"记忆回路"，还是**workflow 结构自我演化的驱动力**。

---

## 五、ActionHistory：执行轨迹记录

### 5.1 模型

`schemas/action_history.py:45-80`：

```python
class ActionHistory(BaseModel):
    action_id: str           # UUID
    role: ActionRole         # system / assistant / user / tool / workflow / interaction
    messages: str            # 思考或推理过程
    action_type: str         # 操作类型（NodeType / MCP tool name / message）
    input: Any               # 输入数据
    output: Any              # 输出数据
    status: ActionStatus     # processing / success / failed
    start_time / end_time    # 时间戳
    depth: int               # 嵌套深度 (0=主流程, 1=sub-agent)
    parent_action_id: str    # 父 action ID
```

### 5.2 ActionHistoryManager

集中管理所有 action 的生命周期，支持：
- 按 action_id 索引查找
- 获取最后 N 个 actions
- 序列化为 dict 用于持久化/展示

每次 LLM 调用、工具调用、节点执行都生成对应的 ActionHistory 记录，形成完整的**执行轨迹链**。这不仅用于调试和可观测性，也在 compact 时作为压缩源数据。

---

## 六、存储层：知识库的持久化记忆

除了运行时的 context/session 管理，Data Engineer Agent 还有一套**知识库（KB）持久化存储**，可以理解为"长期记忆"：

### 6.1 存储模块（LanceDB 向量数据库）

`data_engineer/storage/` 下的模块：

| 模块 | 内容 | 作用 |
|------|------|------|
| `schema_metadata` | 表结构、字段、样本值 | Schema Linking 检索 |
| `semantic_model` | 语义模型定义 | 指标/维度语义理解 |
| `metric` | 指标定义、计算逻辑 | Metrics Search |
| `ext_knowledge` | 外部知识 | 业务术语→SQL映射 |
| `reference_sql` | 参考 SQL 示例 | Few-shot 检索 |
| `reference_template` | SQL 模板 | 模板化 SQL 生成 |
| `document` | 平台文档 (Snowflake/Polaris 等) | 文档 RAG |
| `feedback` | 用户反馈 | 反馈驱动的持续改进 |

### 6.2 存储路径（按项目隔离）

```
{project_root}/subject/
  ├── semantic_models/     # 语义模型 YAML
  ├── sql_summaries/       # SQL 摘要 YAML
  └── ext_knowledge/       # 外部知识 CSV

~/.data_engineer/data/{project_name}/data_engineer_db/   # LanceDB 向量库
```

### 6.3 RAG 检索流程

在 workflow 执行时，`SchemaLinkingNode`、`SearchMetricsNode`、`DocSearchNode` 等节点会从 LanceDB 中检索相关内容注入 Context，形成 **检索增强的工作记忆**。

---

## 七、完整流程示例

一次 SQL 生成任务中，memory/context 的完整流转：

```
用户输入: "上个月每个产品的销售额是多少？"

1. [BeginNode] 初始化 workflow
   └─ Context 创建（空）

2. [DateParserNode] 解析相对时间 → "2026-04"
   └─ 写入 SqlTask.date_ranges

3. [SchemaLinkingNode] 向量检索
   └─ 从 LanceDB 匹配相关表 → Context.table_schemas
   └─ 加载样本数据 → Context.table_values

4. [GenSQLAgenticNode] 生成 SQL
   ├─ 读取 Context.table_schemas + table_values
   ├─ 读取 Context.metrics（指标RAG结果）
   ├─ 注入 memory_context（如果 memory_enabled）
   ├─ 注入 AGENTS.md 项目上下文
   └─ 生成 SQL → 追加 Context.sql_contexts[0]

5. [ExecuteSQLNode] 执行 SQL
   └─ 写入结果 → Context.sql_contexts[0].sql_return

6. [ReflectNode] 评估结果
   ├─ 如果 SUCCESS → 跳过
   ├─ 如果失败 → 策略选择 → 动态插入新节点
   └─ 写回 reflection_strategy → Context.sql_contexts[0]

7. [OutputNode] 输出最终结果
   └─ 保存到 output_dir

8. Session 持久化（如果是 chat 模式）
   └─ AdvancedSQLiteSession 保存对话历史
```

---

## 八、关键设计决策

1. **Sub-agent 默认不启用 memory**：内置 subagent（gen_sql 等）聚焦单次任务，不受历史干扰；chat 节点和用户自定义 subagent 默认启用
2. **Ephemeral vs 持久化 session**：sub-agent 使用 `:memory:` 模式，不产生持久化开销；顶层交互持久化到 `~/.data_engineer/sessions/`
3. **Memory 按 node_name 隔离**：不同节点类型有独立的 memory 目录，chat 和 gen_sql 的 memory 互不干扰
4. **AGENTS.md 作为全局项目上下文**：所有节点共享，前 200 行注入 prompt
5. **Context 是 workflow 级别的**：同一个 workflow 中的所有节点共享同一个 Context，但不同 workflow 完全隔离
6. **Reflection 有最大轮次限制**：防止无限循环，默认 3 轮后强制执行 reasoning 或终止

---

## 九、面试题

### Q1：Data Engineer Agent 的 memory 架构分为哪几层？

**答：四层。** SDK 层用 `AdvancedSQLiteSession` 做对话持久化和自动 compact；Prompt 层按节点类型选择性注入 memory 到 system prompt；Workflow 层用 `Context.sql_contexts` 做任务级工作记忆；反思层用 `ReflectNode` 评估结果并动态调整 workflow。

---

### Q2：`AdvancedSQLiteSession` 的 Ephemeral 和持久化模式有什么区别？

**答：** Ephemeral 是 `:memory:` 纯内存模式，sub-agent 用完即丢，零磁盘开销；持久化模式写入 `~/.data_engineer/sessions/{project}/{session_id}.db`，chat 节点跨会话可恢复。两者的切换只靠一个 `ephemeral` bool 标记。

---

### Q3：为什么 `gen_sql` 等内置 subagent 默认 `memory_enabled = False` 而 `chat` 默认开启？

**答：** 内置 subagent 做原子任务（生成一条 SQL），历史对话会干扰质量，而且 context window 要留给 schema、metrics 等关键信息。chat 节点面向多轮交互，需要记忆上下文。

---

### Q4：`Context.sql_contexts` 的累积机制是怎样的？

**答：** 每轮 SQL 生成→执行→反思后 append 一个 `SQLContext`，包含 SQL、执行结果、错误和反思策略。下一轮 `GenerateSQLNode` 把整条链拼入 prompt，LLM 能看到之前所有的 SQL 和错误，形成 in-context learning 链。本质上是把"我的执行轨迹"变成了 few-shot 示例。

---

### Q5：ReflectNode 有哪些策略？如何防止无限循环？

**答：** 7 种策略——`SUCCESS` / `SIMPLE_REGENERATE` / `SCHEMA_LINKING` / `DOC_SEARCH` / `REASONING` / `COLUMN_EXPLORATION` / `UNKNOWN`，分别对应不同失败原因。防死循环靠 `MAX_REFLECTION_ROUNDS`（默认 3）：第 3 轮强制执行 REASONING，第 4 轮直接终止。

---

### Q6：Memory 注入 system prompt 的完整顺序是什么？

**答：** 每次 prompt 构建走 `_finalize_system_prompt()`：base 模板 → AGENTS.md 项目上下文（前 200 行）→ Skills XML → memory_context（仅 `memory_enabled=True` 的节点，从 `{workspace}/.data_engineer/memory/{node_name}/` 加载）→ 语言约束。整个过程按节点类型决定是否注入 memory。

---

### Q7：为什么 sub-agent 用 Ephemeral session 而不是持久化？

**答：** sub-agent 是临时执行单元，用完即销毁；如果每个都落盘，`sessions/` 目录会快速膨胀，而且 sub-agent 的对话历史不应污染顶层 session。内存 session 更快、更干净。

---

### Q8：`ActionHistory.depth` 字段有什么用？

**答：** depth 标记嵌套层级（0=主流程，1=sub-agent）。compact 时优先压缩 depth>0 的子代理内部细节，保留 depth=0 的用户可见决策点，比纯按时间压缩更智能。

---

### Q9：如何给 Data Engineer Agent 增加"长期用户偏好记忆"？

**答：** 最轻方案是利用现有 `{workspace}/.data_engineer/memory/{node_name}/` 目录放偏好文件，`_inject_memory_context` 自动注入，零代码。进阶可以 LLM 自动提取偏好 → LanceDB 存储 → 向量检索。

---

### Q10：Memory 系统的性能瓶颈在哪？

**答：** 五处：长 session 文件加载慢（靠 compaction）；`sql_contexts` 撑爆 prompt（限制最近 N 个）；LanceDB 大规模检索延迟（分层索引+缓存）；Memory 文件每次 IO（mtime 检测+内存缓存）；ActionHistory 膨胀（按 depth 裁剪）。
