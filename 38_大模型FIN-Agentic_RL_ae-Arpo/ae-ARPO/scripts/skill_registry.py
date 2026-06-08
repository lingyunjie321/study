"""
Agent Skill Registry
====================
Composable skill management system for LLM agents. Provides:
  - Skill definition schema with versioning
  - Registration and discovery (by tag, capability, dependency)
  - Dependency resolution with topological sort
  - Skill chaining / pipeline construction
  - Compatibility with the AEARPO/ARAEPO BaseTool ecosystem

Design rationale:
  A Skill is a higher-level abstraction than a Tool. While Tools provide
  atomic actions (search, execute code), Skills compose multiple tool calls
  and decision logic into reusable capabilities. Skills have:
    - Metadata (name, version, description, tags)
    - Interface (inputs, outputs, trigger conditions)
    - Dependencies (other skills they require)
    - Execution logic (the actual implementation)

Usage:
  # Register skills programmatically
  python scripts/skill_registry.py --demo

  # As importable module
  from scripts.skill_registry import SkillRegistry, Skill, SkillSchema
"""

import hashlib
import importlib
import inspect
import json
import logging
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("skill_registry")


# ---------------------------------------------------------------------------
# Schema & Types
# ---------------------------------------------------------------------------

class SkillCapability(Enum):
    """Category of capability a skill provides."""
    PERCEPTION = "perception"       # Sense environment state
    REASONING = "reasoning"         # Plan, decompose, decide
    ACTION = "action"               # Execute tool calls
    MEMORY = "memory"               # Store/retrieve information
    COMMUNICATION = "communication" # Generate responses
    COORDINATION = "coordination"   # Orchestrate other skills


@dataclass
class SkillSchema:
    """
    Immutable specification of a skill's contract.

    Attributes:
        name: Unique skill identifier (e.g., "web_search_and_summarize")
        version: Semantic version string (MAJOR.MINOR.PATCH)
        display_name: Human-readable name
        description: What the skill does
        tags: Searchable labels for discovery
        capabilities: What category of capability this provides
        inputs: Expected input schema (JSON Schema subset)
        outputs: Output schema (JSON Schema subset)
        trigger_phrases: Natural language triggers for auto-activation
        dependencies: Names of skills this one depends on
        conflict_with: Names of mutually exclusive skills
        priority: Execution priority (higher = earlier in pipelines)
        author: Skill author metadata
    """
    name: str
    version: str
    display_name: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    capabilities: List[SkillCapability] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    trigger_phrases: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    conflict_with: List[str] = field(default_factory=list)
    priority: int = 50
    author: str = ""

    def __post_init__(self):
        if not self.display_name:
            self.display_name = self.name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "display_name": self.display_name,
            "description": self.description,
            "tags": self.tags,
            "capabilities": [c.value for c in self.capabilities],
            "inputs": self.inputs,
            "outputs": self.outputs,
            "trigger_phrases": self.trigger_phrases,
            "dependencies": self.dependencies,
            "conflict_with": self.conflict_with,
            "priority": self.priority,
            "author": self.author,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillSchema":
        caps = [SkillCapability(c) for c in data.get("capabilities", [])]
        return cls(
            name=data["name"],
            version=data["version"],
            display_name=data.get("display_name", ""),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            capabilities=caps,
            inputs=data.get("inputs", {}),
            outputs=data.get("outputs", {}),
            trigger_phrases=data.get("trigger_phrases", []),
            dependencies=data.get("dependencies", []),
            conflict_with=data.get("conflict_with", []),
            priority=data.get("priority", 50),
            author=data.get("author", ""),
        )


# ---------------------------------------------------------------------------
# Skill Base Class
# ---------------------------------------------------------------------------

class BaseSkill(ABC):
    """
    Abstract base for all skills. A skill encapsulates:
      - A schema describing its contract
      - An execute method implementing the skill logic
      - Optional setup/teardown for resource management

    Skills are stateful: they can maintain session-level state across
    multiple invocations within a single agent trajectory.
    """

    def __init__(self):
        self._session_state: Dict[str, Any] = {}
        self._call_count: int = 0
        self._total_duration_ms: float = 0.0

    @property
    @abstractmethod
    def schema(self) -> SkillSchema:
        """Return the skill's schema specification."""
        ...

    @abstractmethod
    def execute(self, inputs: Dict[str, Any],
                context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the skill.

        Args:
            inputs: Skill-specific input parameters.
            context: Shared execution context (tools, memories, config).

        Returns:
            Dict with at least {"status": "success"|"error", "output": ...}
        """
        ...

    def setup(self, context: Optional[Dict[str, Any]] = None):
        """Initialize resources before first execution. Override if needed."""
        self._session_state.clear()
        self._call_count = 0
        self._total_duration_ms = 0.0

    def teardown(self):
        """Release resources. Override if needed."""
        self._session_state.clear()

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "skill_name": self.schema.name,
            "call_count": self._call_count,
            "total_duration_ms": self._total_duration_ms,
        }


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class SkillRegistry:
    """
    Central skill registration and discovery service.

    Manages the lifecycle of skills: register, discover, resolve dependencies,
    and construct execution pipelines.
    """

    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}        # name -> instance
        self._schemas: Dict[str, SkillSchema] = {}     # name -> schema
        self._tag_index: Dict[str, Set[str]] = defaultdict(set)       # tag -> {names}
        self._capability_index: Dict[SkillCapability, Set[str]] = defaultdict(set)

    # ---- Registration ----

    def register(self, skill: BaseSkill) -> bool:
        """
        Register a skill instance. Returns False if a skill with the same name
        and version already exists.

        Raises ValueError if schema validation fails.
        """
        schema = skill.schema
        self._validate_schema(schema)

        key = f"{schema.name}@{schema.version}"
        if schema.name in self._skills:
            existing = self._skills[schema.name].schema
            if existing.version == schema.version:
                logger.warning(
                    f"Skill '{schema.name}' v{schema.version} already registered. "
                    f"Skipping."
                )
                return False
            logger.info(
                f"Upgrading '{schema.name}': v{existing.version} -> v{schema.version}"
            )

        self._skills[schema.name] = skill
        self._schemas[schema.name] = schema

        # Update indices
        for tag in schema.tags:
            self._tag_index[tag.lower()].add(schema.name)
        for cap in schema.capabilities:
            self._capability_index[cap].add(schema.name)

        logger.info(f"Registered skill: {schema.name} v{schema.version}")
        return True

    def unregister(self, name: str):
        """Remove a skill from the registry."""
        if name not in self._skills:
            return

        schema = self._schemas[name]

        # Clean indices
        for tag in schema.tags:
            self._tag_index[tag.lower()].discard(name)
        for cap in schema.capabilities:
            self._capability_index[cap].discard(name)

        del self._skills[name]
        del self._schemas[name]
        logger.info(f"Unregistered skill: {name}")

    # ---- Discovery ----

    def get(self, name: str) -> Optional[BaseSkill]:
        """Get a skill by name."""
        return self._skills.get(name)

    def get_schema(self, name: str) -> Optional[SkillSchema]:
        """Get a skill's schema by name."""
        return self._schemas.get(name)

    def list_all(self) -> List[SkillSchema]:
        """List all registered skill schemas."""
        return list(self._schemas.values())

    def find_by_tag(self, tag: str) -> List[SkillSchema]:
        """Find skills matching a tag (case-insensitive)."""
        names = self._tag_index.get(tag.lower(), set())
        return [self._schemas[n] for n in names]

    def find_by_capability(self, capability: SkillCapability) -> List[SkillSchema]:
        """Find skills providing a specific capability."""
        names = self._capability_index.get(capability, set())
        return [self._schemas[n] for n in names]

    def search(self, query: str) -> List[SkillSchema]:
        """
        Fuzzy search for skills by query string.
        Matches against name, display_name, description, and tags.
        """
        q = query.lower()
        results = []
        for schema in self._schemas.values():
            score = 0
            if q in schema.name.lower():
                score += 10
            if q in schema.display_name.lower():
                score += 8
            if q in schema.description.lower():
                score += 3
            for tag in schema.tags:
                if q in tag.lower():
                    score += 5
            if score > 0:
                results.append((score, schema))
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results]

    # ---- Dependency Resolution ----

    def resolve_dependencies(self, skill_names: List[str]) -> Tuple[
        List[str],  # execution order (topological sort)
        List[str],  # missing dependencies
        List[str],  # circular dependency chain
    ]:
        """
        Resolve dependencies for a set of skills using Kahn's algorithm.

        Returns:
            (execution_order, missing_deps, cycle_chain)
            - execution_order: topologically sorted skill names
            - missing_deps: dependencies that are not registered
            - cycle_chain: non-empty if a circular dependency exists
        """
        # Build adjacency: name -> {dependencies}
        adj: Dict[str, Set[str]] = {}
        in_degree: Dict[str, int] = {}
        all_names = set()

        # Collect all skill names (requested + transitive deps)
        to_process = list(skill_names)
        visited = set()
        missing = []

        while to_process:
            name = to_process.pop()
            if name in visited:
                continue
            visited.add(name)

            schema = self._schemas.get(name)
            if schema is None:
                missing.append(name)
                continue

            for dep in schema.dependencies:
                if dep not in visited:
                    to_process.append(dep)
            all_names.add(name)

        if missing:
            return [], missing, []

        # Build in-degree map
        for name in all_names:
            schema = self._schemas[name]
            deps = {d for d in schema.dependencies if d in all_names}
            adj[name] = deps
            if name not in in_degree:
                in_degree[name] = 0
            for dep in deps:
                in_degree[dep] = in_degree.get(dep, 0) + 1

        # Kahn's algorithm
        queue = deque([n for n in all_names if in_degree.get(n, 0) == 0])
        order = []

        while queue:
            # When multiple skills have in_degree 0, prioritize by priority
            candidates = sorted(queue, key=lambda n: -self._schemas[n].priority)
            queue = deque(candidates)
            node = queue.popleft()
            order.append(node)

            for neighbor in adj.get(node, set()):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(all_names):
            cycle_nodes = [n for n in all_names if n not in order]
            return [], [], cycle_nodes

        return order, [], []

    def check_conflicts(self, skill_names: List[str]) -> List[Tuple[str, str]]:
        """Check for mutual conflicts among a set of skills."""
        conflicts = []
        names_set = set(skill_names)
        for name in skill_names:
            schema = self._schemas.get(name)
            if schema is None:
                continue
            for conflict in schema.conflict_with:
                if conflict in names_set:
                    conflicts.append((name, conflict))
        return conflicts

    # ---- Pipeline Construction ----

    def build_pipeline(self, skill_names: List[str]) -> Optional["SkillPipeline"]:
        """
        Construct an executable pipeline from a list of skill names.
        Handles dependency resolution and ordering automatically.
        """
        order, missing, cycle = self.resolve_dependencies(skill_names)

        if missing:
            logger.error(f"Cannot build pipeline. Missing dependencies: {missing}")
            return None
        if cycle:
            logger.error(f"Cannot build pipeline. Circular dependency: {cycle}")
            return None

        conflicts = self.check_conflicts(order)
        if conflicts:
            logger.error(f"Cannot build pipeline. Conflicts: {conflicts}")
            return None

        skills = [self._skills[name] for name in order]
        return SkillPipeline(skills)

    # ---- Validation ----

    def _validate_schema(self, schema: SkillSchema):
        """Validate a skill schema before registration."""
        if not schema.name or not schema.name.strip():
            raise ValueError("Skill name must not be empty")
        if not schema.version:
            raise ValueError(f"Skill '{schema.name}' must have a version")

        # Validate version format (loose semver)
        parts = schema.version.split(".")
        if len(parts) < 2 or len(parts) > 3:
            raise ValueError(
                f"Skill '{schema.name}': version must be MAJOR.MINOR[.PATCH], "
                f"got '{schema.version}'"
            )
        for part in parts:
            if not part.isdigit():
                raise ValueError(
                    f"Skill '{schema.name}': version parts must be integers"
                )

    @property
    def size(self) -> int:
        return len(self._skills)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class SkillPipeline:
    """
    Ordered sequence of skills that execute in series.
    Each skill's output becomes part of the context for subsequent skills.

    Supports:
      - Sequential execution with context propagation
      - Early termination on errors
      - Execution tracing
    """

    def __init__(self, skills: List[BaseSkill]):
        if not skills:
            raise ValueError("Pipeline requires at least one skill")
        self.skills = skills
        self.schemas = [s.schema for s in skills]

    def execute(self, initial_inputs: Dict[str, Any],
                shared_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute skills in order, passing outputs forward.

        Returns:
            {
                "status": "success"|"partial_failure"|"failure",
                "results": [per-skill results],
                "final_output": ...,
                "trace": [execution traces],
            }
        """
        context = shared_context or {}
        context.setdefault("pipeline_state", {})
        context.setdefault("_history", [])

        results = []
        current_inputs = initial_inputs
        has_failure = False

        for i, skill in enumerate(self.skills):
            schema = skill.schema
            logger.debug(f"Pipeline [{i+1}/{len(self.skills)}]: {schema.name}")

            try:
                output = skill.execute(current_inputs, context)
                results.append({
                    "skill": schema.name,
                    "status": output.get("status", "unknown"),
                    "output": output,
                })

                if output.get("status") == "error":
                    has_failure = True
                    if not output.get("continue_on_error", False):
                        break

                # Propagate output as input to next skill
                current_inputs = {**current_inputs, **output.get("output", {})}

            except Exception as e:
                logger.error(f"Skill '{schema.name}' raised exception: {e}")
                results.append({
                    "skill": schema.name,
                    "status": "error",
                    "error": str(e),
                })
                has_failure = True
                break

        status = "failure" if has_failure and not results else \
                 "partial_failure" if has_failure else "success"

        return {
            "status": status,
            "results": results,
            "final_output": current_inputs,
            "trace": context.get("_history", []),
            "skills_executed": len(results),
            "total_skills": len(self.skills),
        }

    @property
    def total_skills(self) -> int:
        return len(self.skills)

    def describe(self) -> str:
        """Return a human-readable pipeline description."""
        names = [s.display_name for s in self.schemas]
        return " -> ".join(names)


# ---------------------------------------------------------------------------
# Built-in Example Skills
# ---------------------------------------------------------------------------

class WebSearchSkill(BaseSkill):
    """Search the web and return structured results."""

    @property
    def schema(self) -> SkillSchema:
        return SkillSchema(
            name="web_search",
            version="1.0.0",
            display_name="Web Search",
            description="Execute web search queries and return ranked results "
                        "with snippets and URLs.",
            tags=["search", "web", "information_retrieval"],
            capabilities=[SkillCapability.ACTION, SkillCapability.PERCEPTION],
            inputs={
                "query": {"type": "string", "description": "Search query"},
                "num_results": {"type": "integer", "default": 5},
            },
            outputs={
                "results": {"type": "array", "items": {
                    "type": "object", "properties": {
                        "title": "string", "url": "string", "snippet": "string"
                    }
                }}
            },
            trigger_phrases=["search for", "look up", "find information about"],
            priority=80,
        )

    def execute(self, inputs, context=None):
        query = inputs.get("query", "")
        num = inputs.get("num_results", 5)
        # In production, call actual search API
        return {
            "status": "success",
            "output": {
                "results": [
                    {"title": f"Result {i} for: {query}",
                     "url": f"https://example.com/{i}",
                     "snippet": f"Content about {query}..."}
                    for i in range(min(num, 3))
                ]
            }
        }


class SummarizationSkill(BaseSkill):
    """Summarize retrieved text into concise key points."""

    @property
    def schema(self) -> SkillSchema:
        return SkillSchema(
            name="text_summarization",
            version="1.0.0",
            display_name="Text Summarization",
            description="Condense long texts into structured summaries "
                        "with key points, entities, and sentiment.",
            tags=["nlp", "summarization", "text_processing"],
            capabilities=[SkillCapability.REASONING],
            inputs={
                "text": {"type": "string", "description": "Text to summarize"},
                "max_points": {"type": "integer", "default": 3},
            },
            outputs={
                "summary": {"type": "string"},
                "key_points": {"type": "array", "items": {"type": "string"}},
            },
            trigger_phrases=["summarize", "give me the gist", "tl;dr"],
            dependencies=[],  # Can also chain after search: ["web_search"]
            priority=60,
        )

    def execute(self, inputs, context=None):
        text = inputs.get("text", "")[:500]
        max_points = inputs.get("max_points", 3)
        return {
            "status": "success",
            "output": {
                "summary": f"Summary of text ({len(text)} chars)...",
                "key_points": [f"Key point {i+1}" for i in range(max_points)],
            }
        }


class FactCheckSkill(BaseSkill):
    """Verify claims against known facts or retrieved evidence."""

    @property
    def schema(self) -> SkillSchema:
        return SkillSchema(
            name="fact_check",
            version="1.0.0",
            display_name="Fact Checker",
            description="Verify factual claims by cross-referencing evidence. "
                        "Returns a confidence score and supporting citations.",
            tags=["verification", "fact_checking", "quality"],
            capabilities=[SkillCapability.REASONING],
            inputs={
                "claim": {"type": "string", "description": "Claim to verify"},
                "evidence": {"type": "array", "description": "Supporting texts"},
            },
            outputs={
                "verdict": {"type": "string", "enum": ["supported", "refuted", "uncertain"]},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "citations": {"type": "array"},
            },
            trigger_phrases=["fact check", "verify", "is it true that"],
            dependencies=["web_search"],
            priority=50,
        )

    def execute(self, inputs, context=None):
        claim = inputs.get("claim", "")
        return {
            "status": "success",
            "output": {
                "verdict": "uncertain",
                "confidence": 0.6,
                "citations": [],
                "reasoning": f"Claim '{claim[:100]}' requires more evidence.",
            }
        }


class RAGSkill(BaseSkill):
    """
    RAG (Retrieval-Augmented Generation) skill.
    Retrieves relevant context and generates grounded responses.
    """

    @property
    def schema(self) -> SkillSchema:
        return SkillSchema(
            name="rag_qa",
            version="1.0.0",
            display_name="RAG Question Answering",
            description="Retrieve relevant documents and generate answers "
                        "grounded in retrieved evidence. Reduces hallucination "
                        "by anchoring responses in source material.",
            tags=["rag", "qa", "knowledge", "retrieval"],
            capabilities=[SkillCapability.REASONING, SkillCapability.ACTION],
            inputs={
                "question": {"type": "string"},
                "top_k": {"type": "integer", "default": 5},
            },
            outputs={
                "answer": {"type": "string"},
                "sources": {"type": "array"},
                "confidence": {"type": "number"},
            },
            trigger_phrases=["according to the documents", "based on the knowledge base"],
            dependencies=["web_search"],
            priority=70,
        )

    def execute(self, inputs, context=None):
        question = inputs.get("question", "")
        return {
            "status": "success",
            "output": {
                "answer": f"Based on retrieved documents, the answer to "
                          f"'{question[:80]}' is...",
                "sources": [{"doc_id": "doc_1", "relevance": 0.92}],
                "confidence": 0.85,
            }
        }


class MemoryStoreSkill(BaseSkill):
    """Persist information to agent memory for later retrieval."""

    @property
    def schema(self) -> SkillSchema:
        return SkillSchema(
            name="memory_store",
            version="1.0.0",
            display_name="Memory Store",
            description="Store key-value pairs and structured facts in "
                        "agent memory for cross-turn persistence.",
            tags=["memory", "storage", "persistence"],
            capabilities=[SkillCapability.MEMORY],
            inputs={
                "key": {"type": "string"},
                "value": {"type": "object"},
                "ttl": {"type": "integer", "description": "Time-to-live in seconds"},
            },
            outputs={
                "stored": {"type": "boolean"},
                "key": {"type": "string"},
            },
            trigger_phrases=["remember", "store this", "save for later"],
            priority=90,
        )

    def execute(self, inputs, context=None):
        key = inputs.get("key", "")
        value = inputs.get("value", {})
        self._session_state[key] = value
        return {
            "status": "success",
            "output": {"stored": True, "key": key}
        }


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def run_demo():
    """Demonstrate the skill registry with sample skills and pipelines."""
    print("=" * 60)
    print("  Agent Skill Registry — Demonstration")
    print("=" * 60)

    # Create registry
    registry = SkillRegistry()

    # Register built-in skills
    skills = [
        WebSearchSkill(),
        SummarizationSkill(),
        FactCheckSkill(),
        RAGSkill(),
        MemoryStoreSkill(),
    ]
    for skill in skills:
        registry.register(skill)

    print(f"\nRegistered {registry.size} skills")

    # List all
    print("\n--- Registered Skills ---")
    for schema in registry.list_all():
        print(f"  [{schema.version}] {schema.display_name}")
        print(f"    tags: {', '.join(schema.tags)}")
        print(f"    capabilities: {[c.value for c in schema.capabilities]}")
        if schema.dependencies:
            print(f"    depends on: {', '.join(schema.dependencies)}")

    # Search
    print("\n--- Search: 'rag' ---")
    for schema in registry.search("rag"):
        print(f"  {schema.display_name}: {schema.description}")

    # Find by tag
    print("\n--- Skills tagged 'search' ---")
    for schema in registry.find_by_tag("search"):
        print(f"  {schema.name} v{schema.version}")

    # Dependency resolution
    print("\n--- Dependency Resolution: fact_check ---")
    order, missing, cycle = registry.resolve_dependencies(["fact_check"])
    if missing:
        print(f"  Missing: {missing}")
    elif cycle:
        print(f"  Cycle: {cycle}")
    else:
        print(f"  Execution order: {order}")

    # Build pipeline
    print("\n--- Pipeline: web_search -> text_summarization ---")
    pipeline = registry.build_pipeline(["web_search", "text_summarization"])
    if pipeline:
        print(f"  Pipeline: {pipeline.describe()}")
        result = pipeline.execute({"query": "What is AEARPO?"})
        print(f"  Status: {result['status']}")
        print(f"  Skills executed: {result['skills_executed']}/{result['total_skills']}")
        for r in result["results"]:
            print(f"    [{r['status']}] {r['skill']}")

    # Conflict check
    print("\n--- Conflict Check ---")
    conflicts = registry.check_conflicts(["web_search", "text_summarization"])
    if conflicts:
        print(f"  Conflicts found: {conflicts}")
    else:
        print("  No conflicts detected")

    # Export full registry
    print("\n--- Registry Export (first 500 chars) ---")
    export_data = {
        "skills": [s.to_dict() for s in registry.list_all()],
        "total_count": registry.size,
    }
    export_str = json.dumps(export_data, ensure_ascii=False, indent=2)
    print(export_str[:500] + "...")

    print("\nDemo complete. Skill registry is ready for integration.")
    return registry


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Agent Skill Registry — composable skill management"
    )
    parser.add_argument("--demo", action="store_true",
                        help="Run demonstration with sample skills")
    parser.add_argument("--export", type=str, metavar="FILE",
                        help="Export registry to JSON file")
    parser.add_argument("--list", action="store_true",
                        help="List all registered skills")

    args = parser.parse_args()

    registry = SkillRegistry()

    # Always register built-in skills in demo/list mode
    if args.demo or args.list:
        for skill_cls in [WebSearchSkill, SummarizationSkill, FactCheckSkill,
                          RAGSkill, MemoryStoreSkill]:
            registry.register(skill_cls())

    if args.demo:
        run_demo()
    elif args.list:
        for schema in registry.list_all():
            print(f"{schema.name}@{schema.version} — {schema.description}")
    elif args.export:
        for skill_cls in [WebSearchSkill, SummarizationSkill, FactCheckSkill,
                          RAGSkill, MemoryStoreSkill]:
            registry.register(skill_cls())
        data = {
            "skills": [s.to_dict() for s in registry.list_all()],
            "total_count": registry.size,
        }
        with open(args.export, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Exported {registry.size} skills to {args.export}")
    else:
        parser.print_help()
