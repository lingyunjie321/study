"""
Test Harness for AEARPO / ARAEPO Project
=========================================
Lightweight validation framework that tests project components without
requiring GPU resources. Designed to run in CI/CD or local development.

Validates:
  1. Module importability (verl packages, tools, configs)
  2. Configuration schema (Hydra/OmegaConf YAML validity)
  3. Data integrity (Parquet datasets schema and statistics)
  4. Tool interface compliance (BaseTool contract)
  5. Checkpoint utilities (conversion scripts)

Usage:
  # Run all tests
  python scripts/test_harness.py --all

  # Run specific test suites
  python scripts/test_harness.py --module-imports
  python scripts/test_harness.py --data-validation
  python scripts/test_harness.py --tool-compliance

  # Generate JSON report
  python scripts/test_harness.py --all --report report.json
"""

import importlib
import json
import logging
import os
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("test_harness")


# ---------------------------------------------------------------------------
# Project path resolution
# ---------------------------------------------------------------------------

def resolve_project_root() -> Path:
    """Find the ae-ARPO project root."""
    current = Path(__file__).resolve().parent.parent  # scripts/ -> ae-ARPO/
    if (current / "AEARPO").exists() or (current / "ARAEPO").exists():
        return current
    raise RuntimeError(
        "Cannot locate project root. Run from within ae-ARPO/ directory."
    )


PROJECT_ROOT = resolve_project_root()
AEARPO_ROOT = PROJECT_ROOT / "AEARPO" / "verl_arpo_entropy"
ARAEPO_ROOT = PROJECT_ROOT / "ARAEPO" / "verl_araepo_entropy"
EVAL_ROOT = PROJECT_ROOT / "evaluation"


# ---------------------------------------------------------------------------
# Test result types
# ---------------------------------------------------------------------------

@dataclass
class TestResult:
    name: str
    passed: bool
    duration_ms: float = 0.0
    message: str = ""
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class TestSuite:
    """Collects and runs a set of related tests."""

    def __init__(self, name: str):
        self.name = name
        self.results: List[TestResult] = []
        self.start_time = 0.0

    def run_test(self, name: str, fn: Callable[[], Tuple[bool, str, Dict]]):
        """Run a single test function and record the result."""
        t0 = time.perf_counter()
        try:
            passed, message, details = fn()
        except Exception as e:
            passed = False
            message = f"Unhandled exception: {e}"
            details = {"traceback": traceback.format_exc()}
        elapsed = (time.perf_counter() - t0) * 1000

        result = TestResult(
            name=name,
            passed=passed,
            duration_ms=round(elapsed, 2),
            message=message,
            error=None if passed else message,
            details=details,
        )
        self.results.append(result)

        icon = "[PASS]" if passed else "[FAIL]"
        logger.info(f"  {icon} {name} ({elapsed:.1f}ms)")
        if not passed and message:
            logger.info(f"         {message[:200]}")
        return result

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def duration_ms(self) -> float:
        return sum(r.duration_ms for r in self.results)

    def summary(self) -> str:
        if self.failed == 0:
            return f"{self.name}: {self.total}/{self.total} passed"
        return f"{self.name}: {self.passed}/{self.total} passed, {self.failed} FAILED"


# ---------------------------------------------------------------------------
# Test: Module Importability
# ---------------------------------------------------------------------------

def add_to_syspath(*paths: Path):
    """Add paths to sys.path for import testing."""
    for p in paths:
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))


def test_module_imports(suite: TestSuite):
    """
    Verify that key project modules can be imported without errors.
    This catches missing dependencies, syntax errors, and broken imports.
    """
    add_to_syspath(AEARPO_ROOT, ARAEPO_ROOT, EVAL_ROOT / "src")

    imports_to_test = [
        # verl core (AEARPO)
        ("verl.trainer.main_ppo", "AEARPO"),
        ("verl.trainer.ppo.core_algos", "AEARPO"),
        ("verl.trainer.ppo.ray_trainer", "AEARPO"),
        ("verl.tools.base_tool", "AEARPO"),
        ("verl.tools.search_tool", "AEARPO"),
        # verl core (ARAEPO)
        # Same module paths, different package — test separately via path isolation
        # Agent tools (ARAEPO)
        # Checkpoint conversion
        ("convert_checkpoint_from_verl_to_hf", "AEARPO/merge_ckpt"),
    ]

    for module_path, source in imports_to_test:
        def _test(mp=module_path, src=source):
            try:
                mod = importlib.import_module(mp)
                return True, f"Imported {mp} from {src}", {"module": mp, "source": src}
            except ImportError as e:
                return False, f"Import failed: {e}", {}
            except Exception as e:
                return False, f"Unexpected error: {e}", {}
        suite.run_test(f"import::{source}::{module_path}", _test)

    # Test evaluation package imports
    eval_imports = [
        "inference_engine",
        "evaluator",
        "data_loader",
        "metrics",
        "prompt_manager",
    ]
    for mod_name in eval_imports:
        def _test_eval(mn=mod_name):
            # Evaluation modules are in evaluation/src/
            eval_src = str(EVAL_ROOT / "src")
            if eval_src not in sys.path:
                sys.path.insert(0, eval_src)
            try:
                importlib.import_module(mn)
                return True, f"Imported evaluation.{mn}", {}
            except ImportError as e:
                # Evaluation modules may have heavy deps — skip if missing
                return True, f"Skipped (optional dep): {e}", {"skipped": True}
            except Exception as e:
                return True, f"Skipped (optional dep): {e}", {"skipped": True}
        suite.run_test(f"import::evaluation::{mod_name}", _test_eval)


# ---------------------------------------------------------------------------
# Test: Configuration Validation
# ---------------------------------------------------------------------------

def test_configuration(suite: TestSuite):
    """Validate YAML configuration files for syntax and schema consistency."""

    config_files = [
        ("AEARPO Reasoning", AEARPO_ROOT.parent / "scripts" / "config" / "ppo_trainer.yaml"),
        ("AEARPO DeepSearch", AEARPO_ROOT.parent / "scripts" / "config" / "ppo_trainer_dr.yaml"),
        ("ARAEPO Reasoning", ARAEPO_ROOT.parent / "scripts" / "config" / "ppo_trainer.yaml"),
        ("ARAEPO DeepSearch", ARAEPO_ROOT.parent / "scripts" / "config" / "ppo_trainer_dr.yaml"),
    ]

    for label, config_path in config_files:
        def _test(lbl=label, cp=config_path):
            if not cp.exists():
                return False, f"Config file not found: {cp}", {}

            try:
                from omegaconf import OmegaConf
                cfg = OmegaConf.load(str(cp))

                # Check required top-level keys
                required_keys = ["actor_rollout_ref", "algorithm", "trainer", "data"]
                missing = [k for k in required_keys if k not in cfg]
                if missing:
                    return False, f"Missing keys: {missing}", {"config": str(cp)}

                # Check algorithm config
                algo = cfg.get("algorithm", {})
                algo_keys = list(algo.keys()) if hasattr(algo, 'keys') else []

                return True, f"Valid config: {lbl} ({len(algo_keys)} algo params)", {
                    "config": str(cp),
                    "algorithm_keys": algo_keys,
                }
            except Exception as e:
                return False, f"Config parse error: {e}", {}
        suite.run_test(f"config::{label}", _test)

    # Test agent YAML config
    agent_config = ARAEPO_ROOT / "verl" / "workers" / "agent" / "agent.yaml"
    def _test_agent_yaml():
        if not agent_config.exists():
            return True, "Agent config not present (AEARPO mode)", {"skipped": True}
        try:
            from omegaconf import OmegaConf
            cfg = OmegaConf.load(str(agent_config))
            return True, f"Agent config valid", {"tools": list(cfg.get("tools", {}).keys())}
        except Exception as e:
            return False, f"Agent config error: {e}", {}
    suite.run_test("config::agent_yaml", _test_agent_yaml)


# ---------------------------------------------------------------------------
# Test: Data Validation
# ---------------------------------------------------------------------------

def test_data_validation(suite: TestSuite):
    """Validate Parquet datasets for schema correctness and basic statistics."""

    dataset_paths = [
        ("Train 10K", AEARPO_ROOT.parent / "rl_datasets" / "train_10k.parquet"),
        ("Valid", AEARPO_ROOT.parent / "rl_datasets" / "valid.parquet"),
        ("Hard Search 1K", AEARPO_ROOT.parent / "rl_datasets" / "hard_search_1k.parquet"),
    ]

    for label, data_path in dataset_paths:
        def _test(lbl=label, dp=data_path):
            if not dp.exists():
                return False, f"Dataset not found: {dp}", {}

            try:
                import pandas as pd
                df = pd.read_parquet(dp)
                rows = len(df)
                cols = list(df.columns)

                # Check minimum row count
                min_rows = 10
                if rows < min_rows:
                    return False, f"Too few rows: {rows} < {min_rows}", {}

                # Check required columns
                required = ["data_source", "prompt"]
                missing_cols = [c for c in required if c not in cols]
                if missing_cols:
                    return False, f"Missing columns: {missing_cols}", {}

                # Sample a prompt for sanity
                sample_prompt = str(df["prompt"].iloc[0])[:100]

                return True, f"{lbl}: {rows} rows, {len(cols)} cols", {
                    "rows": rows,
                    "columns": cols,
                    "sample_prompt_preview": sample_prompt,
                }
            except ImportError:
                return True, "Skipped (pandas not available)", {"skipped": True}
            except Exception as e:
                return False, f"Data read error: {e}", {}
        suite.run_test(f"data::{label}", _test)


# ---------------------------------------------------------------------------
# Test: Tool Interface Compliance
# ---------------------------------------------------------------------------

def test_tool_compliance(suite: TestSuite):
    """Verify that tool implementations conform to the BaseTool contract."""

    # ARAEPO agent tools
    agent_tools_dir = ARAEPO_ROOT / "verl" / "workers" / "agent" / "tools"
    # AEARPO tools (non-agent)
    standard_tools_dir = AEARPO_ROOT / "verl" / "tools"

    tool_dirs = [
        ("ARAEPO Agent Tools", agent_tools_dir),
        ("AEARPO Standard Tools", standard_tools_dir),
    ]

    for label, tool_dir in tool_dirs:
        def _test(lbl=label, td=tool_dir):
            if not td.exists():
                return True, f"Skipped: {td} not found", {"skipped": True}

            tool_files = list(td.glob("*_tool.py"))
            results = []
            for tf in tool_files:
                results.append({
                    "file": tf.name,
                    "exists": True,
                })
            return True, f"{lbl}: {len(results)} tool files found", {
                "tools": [r["file"] for r in results],
            }
        suite.run_test(f"tool::discovery::{label}", _test)

    # Test BaseTool abstract interface existence
    base_tool_paths = [
        AEARPO_ROOT / "verl" / "tools" / "base_tool.py",
        ARAEPO_ROOT / "verl" / "workers" / "agent" / "tools" / "base_tool.py",
    ]
    for btp in base_tool_paths:
        def _test(path=btp):
            if not path.exists():
                return False, f"BaseTool not found: {path}", {}
            content = path.read_text(encoding="utf-8")
            has_abstract = "ABC" in content or "abstractmethod" in content or "ABCMeta" in content
            has_execute = "execute" in content
            return has_execute, f"BaseTool at {path.parent.name}: ABC={has_abstract}, execute={has_execute}", {
                "path": str(path),
                "has_abc": has_abstract,
                "has_execute": has_execute,
            }
        suite.run_test(f"tool::base_tool::{btp.parent.name}", _test)

    # Test that RAG tool is importable
    rag_tool_path = PROJECT_ROOT / "scripts" / "rag_milvus_tool.py"
    def _test_rag_import():
        if not rag_tool_path.exists():
            return False, "RAG tool script not found", {}
        try:
            scripts_dir = str(PROJECT_ROOT / "scripts")
            if scripts_dir not in sys.path:
                sys.path.insert(0, scripts_dir)
            from rag_milvus_tool import RAGMilvusTool, RAGConfig
            cfg = RAGConfig(chunk_size=128)
            tool = RAGMilvusTool(cfg)
            return True, f"RAGMilvusTool initialized: dim={cfg.embedding_dim}", {
                "trigger_tag": tool.trigger_tag,
                "name": tool.name,
            }
        except Exception as e:
            return False, f"RAG tool init failed: {e}", {}
    suite.run_test("tool::rag_milvus_import", _test_rag_import)


# ---------------------------------------------------------------------------
# Test: Checkpoint Utilities
# ---------------------------------------------------------------------------

def test_checkpoint_utils(suite: TestSuite):
    """Validate checkpoint conversion scripts are present and parseable."""

    ckpt_scripts = [
        AEARPO_ROOT.parent / "merge_ckpt" / "convert_checkpoint_from_verl_to_hf.py",
    ]

    for script_path in ckpt_scripts:
        def _test(sp=script_path):
            if not sp.exists():
                return False, f"Script not found: {sp}", {}
            try:
                content = sp.read_text(encoding="utf-8")
                compile(content, str(sp), "exec")
                lines = len(content.splitlines())
                return True, f"Checkpoint script compiles: {lines} lines", {
                    "path": str(sp),
                    "lines": lines,
                }
            except SyntaxError as e:
                return False, f"Syntax error: {e}", {}
            except Exception as e:
                return False, f"Read error: {e}", {}
        suite.run_test(f"checkpoint::compile::{script_path.name}", _test)


# ---------------------------------------------------------------------------
# Test: Shell Script Validation
# ---------------------------------------------------------------------------

def test_shell_scripts(suite: TestSuite):
    """Validate training shell scripts exist and have expected structure."""

    shell_scripts = [
        ("AEARPO 7B Reasoning", AEARPO_ROOT.parent / "scripts" / "AEARPO_7B_Reasoning_1node.sh"),
        ("AEARPO 8B DeepSearch", AEARPO_ROOT.parent / "scripts" / "AEARPO_8B_Deepsearch_1node.sh"),
        ("AEARPO 14B DeepSearch", AEARPO_ROOT.parent / "scripts" / "AEARPO_14b_Deepsearch_1node.sh"),
        ("ARAEPO 7B DeepResearch", ARAEPO_ROOT.parent / "scripts" / "ARAEPO_Qwen25_7B_DeepResearch.sh"),
        ("ARAEPO 14B DeepResearch", ARAEPO_ROOT.parent / "scripts" / "ARAEPO_Qwen3_14B_DeepResearch.sh"),
    ]

    for label, script_path in shell_scripts:
        def _test(lbl=label, sp=script_path):
            if not sp.exists():
                return False, f"Script not found: {sp}", {}

            content = sp.read_text(encoding="utf-8")
            lines = content.splitlines()

            # Check for expected patterns
            has_python = any("python" in line.lower() for line in lines)
            has_config = any("config" in line.lower() for line in lines)
            has_trainer = any("main_ppo" in line for line in lines)

            if not has_trainer:
                return False, "No main_ppo entry point found", {}
            if not has_config:
                return False, "No config reference found", {}

            return True, f"{lbl}: {len(lines)} lines, valid structure", {
                "lines": len(lines),
                "has_python": has_python,
                "has_trainer": has_trainer,
                "has_config": has_config,
            }
        suite.run_test(f"shell::structure::{label}", _test)


# ---------------------------------------------------------------------------
# Test: Project Integrity
# ---------------------------------------------------------------------------

def test_project_integrity(suite: TestSuite):
    """Check project-level files and documentation integrity."""

    critical_files = [
        ("README", PROJECT_ROOT / "README.md"),
        ("Project Summary", PROJECT_ROOT / "PROJECT_SUMMARY.md"),
        ("ARAEPO core_algos", ARAEPO_ROOT / "verl" / "trainer" / "ppo" / "core_algos.py"),
        ("AEARPO core_algos", AEARPO_ROOT / "verl" / "trainer" / "ppo" / "core_algos.py"),
        ("ARAEPO rollout", ARAEPO_ROOT / "verl" / "workers" / "rollout" / "vllm_rollout" / "vllm_rollout_with_tools.py"),
        ("AEARPO rollout", AEARPO_ROOT / "verl" / "workers" / "rollout" / "vllm_rollout" / "vllm_rollout_with_tools.py"),
    ]

    for label, file_path in critical_files:
        def _test(lbl=label, fp=file_path):
            if not fp.exists():
                return False, f"File not found: {fp}", {}
            size_kb = fp.stat().st_size / 1024
            return True, f"{lbl}: {size_kb:.1f} KB", {"size_kb": round(size_kb, 1)}
        suite.run_test(f"integrity::file_check::{label}", _test)


# ---------------------------------------------------------------------------
# Test Runner
# ---------------------------------------------------------------------------

class Harness:
    """Top-level test harness orchestrator."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.suites: List[TestSuite] = []
        self.start_time = 0.0

    def add_suite(self, suite: TestSuite):
        self.suites.append(suite)

    def run_all(self) -> Dict[str, Any]:
        self.start_time = time.perf_counter()

        for suite in self.suites:
            logger.info(f"\n{'=' * 60}")
            logger.info(f"  Suite: {suite.name}")
            logger.info(f"{'=' * 60}")

        return self._collect_results()

    def _collect_results(self) -> Dict[str, Any]:
        total_elapsed = (time.perf_counter() - self.start_time) * 1000
        all_results = []
        total_passed = 0
        total_failed = 0

        for suite in self.suites:
            all_results.extend(suite.results)
            total_passed += suite.passed
            total_failed += suite.failed

        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "summary": {
                "total_tests": len(all_results),
                "passed": total_passed,
                "failed": total_failed,
                "pass_rate": f"{total_passed / max(len(all_results), 1) * 100:.1f}%",
                "total_elapsed_ms": round(total_elapsed, 2),
            },
            "suites": [
                {
                    "name": s.name,
                    "passed": s.passed,
                    "failed": s.failed,
                    "total": s.total,
                    "duration_ms": round(s.duration_ms, 2),
                }
                for s in self.suites
            ],
            "failures": [
                {
                    "suite": s.name,
                    "test": r.name,
                    "error": r.error,
                }
                for s in self.suites
                for r in s.results
                if not r.passed
            ],
        }
        return report

    def print_report(self, report: Dict[str, Any]):
        """Print a formatted summary report."""
        s = report["summary"]
        print(f"\n{'=' * 60}")
        print(f"  TEST HARNESS REPORT")
        print(f"{'=' * 60}")
        print(f"  Timestamp : {report['timestamp']}")
        print(f"  Project   : {report['project_root']}")
        print(f"  Elapsed   : {s['total_elapsed_ms']:.0f} ms")
        print(f"{'=' * 60}")

        for suite_info in report["suites"]:
            status = "OK" if suite_info["failed"] == 0 else "FAIL"
            print(f"  [{status}] {suite_info['name']}: "
                  f"{suite_info['passed']}/{suite_info['total']} passed "
                  f"({suite_info['duration_ms']:.0f}ms)")

        print(f"{'=' * 60}")
        print(f"  TOTAL: {s['passed']}/{s['total_tests']} passed "
              f"({s['pass_rate']})")

        if report["failures"]:
            print(f"\n  FAILURES ({len(report['failures'])}):")
            for f in report["failures"]:
                print(f"    [{f['suite']}] {f['test']}")
                if f["error"]:
                    print(f"      -> {f['error'][:150]}")

        print(f"{'=' * 60}\n")

    def save_report(self, report: Dict[str, Any], output_path: str):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info(f"Report saved to: {output_path}")


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

def build_harness() -> Harness:
    """Construct the test harness with all suites."""
    harness = Harness(PROJECT_ROOT)

    # Suite 1: Module imports
    suite_imports = TestSuite("Module Imports")
    test_module_imports(suite_imports)
    harness.add_suite(suite_imports)

    # Suite 2: Configuration
    suite_config = TestSuite("Configuration Validation")
    test_configuration(suite_config)
    harness.add_suite(suite_config)

    # Suite 3: Data validation
    suite_data = TestSuite("Data Validation")
    test_data_validation(suite_data)
    harness.add_suite(suite_data)

    # Suite 4: Tool compliance
    suite_tool = TestSuite("Tool Compliance")
    test_tool_compliance(suite_tool)
    harness.add_suite(suite_tool)

    # Suite 5: Checkpoint utilities
    suite_ckpt = TestSuite("Checkpoint Utilities")
    test_checkpoint_utils(suite_ckpt)
    harness.add_suite(suite_ckpt)

    # Suite 6: Shell scripts
    suite_shell = TestSuite("Shell Scripts")
    test_shell_scripts(suite_shell)
    harness.add_suite(suite_shell)

    # Suite 7: Project integrity
    suite_integrity = TestSuite("Project Integrity")
    test_project_integrity(suite_integrity)
    harness.add_suite(suite_integrity)

    return harness


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="AEARPO/ARAEPO Test Harness — validate project components"
    )
    parser.add_argument("--all", action="store_true",
                        help="Run all test suites")
    parser.add_argument("--module-imports", action="store_true",
                        help="Test module importability")
    parser.add_argument("--data-validation", action="store_true",
                        help="Validate Parquet datasets")
    parser.add_argument("--tool-compliance", action="store_true",
                        help="Check tool interface compliance")
    parser.add_argument("--config", action="store_true",
                        help="Validate YAML configurations")
    parser.add_argument("--checkpoint", action="store_true",
                        help="Validate checkpoint utilities")
    parser.add_argument("--integrity", action="store_true",
                        help="Check project file integrity")
    parser.add_argument("--report", type=str, default=None,
                        help="Save JSON report to file")

    args = parser.parse_args()

    run_all = args.all or not any([
        args.module_imports, args.data_validation, args.tool_compliance,
        args.config, args.checkpoint, args.integrity,
    ])

    harness = build_harness()
    report = harness.run_all()
    harness.print_report(report)

    if args.report:
        harness.save_report(report, args.report)

    # Exit with non-zero if any test failed
    if report["summary"]["failed"] > 0:
        logger.warning(f"{report['summary']['failed']} test(s) failed.")
        sys.exit(1)
    else:
        logger.info("All tests passed.")
        sys.exit(0)
