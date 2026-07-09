import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "tools" / "trajectory_provenance.py"
SPEC = importlib.util.spec_from_file_location("trajectory_provenance", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class TrajectoryProvenanceTests(unittest.TestCase):
    def report(self, rows, markers=()):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trajectory.jsonl"
            path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            return MODULE.build_report([path], list(markers))

    def test_declared_reference_before_write_is_confirmed(self):
        report = self.report(
            [
                {"task_id": "a", "tool": "web", "input": {"url": "https://github.com/acme/app/pull/42"}},
                {"task_id": "a", "tool": "apply_patch", "input": {"patch": "fix"}},
                {"task_id": "a", "event": "result", "passed": True},
            ],
            markers=["github.com/acme/app/pull/42"],
        )
        self.assertEqual(report["tasks"][0]["verdict"], "RED_CONFIRMED_RETRIEVAL_BEFORE_DERIVATION")
        self.assertEqual(report["summary"]["confirmed_retrieval_passes"], 1)

    def test_reference_after_first_write_does_not_trigger(self):
        report = self.report(
            [
                {"task_id": "a", "tool": "write_file", "input": {"path": "fix.py"}},
                {"task_id": "a", "tool": "web", "input": {"url": "https://github.com/acme/app/pull/42"}},
                {"task_id": "a", "event": "result", "passed": True},
            ],
            markers=["github.com/acme/app/pull/42"],
        )
        self.assertEqual(report["tasks"][0]["verdict"], "NO_SIGNAL_NOT_PROOF_OF_DERIVATION")

    def test_generic_history_mining_is_yellow_not_red(self):
        report = self.report(
            [
                {"tool": "shell", "input": {"command": "git log -p -- src/core.py"}},
                {"tool": "apply_patch", "input": {"patch": "fix"}},
                {"event": "result", "status": "passed"},
            ]
        )
        self.assertEqual(report["tasks"][0]["verdict"], "YELLOW_SUSPICIOUS_PROVENANCE")
        self.assertEqual(report["summary"]["confirmed_retrieval_passes"], 0)

    def test_clean_run_is_no_signal_not_green_proof(self):
        report = self.report(
            [
                {"tool": "read_file", "input": {"path": "src/core.py"}},
                {"tool": "write_file", "input": {"path": "src/core.py"}},
                {"event": "result", "passed": True},
            ]
        )
        self.assertEqual(report["tasks"][0]["verdict"], "NO_SIGNAL_NOT_PROOF_OF_DERIVATION")

    def test_summary_groups_tasks_and_strips_confirmed_passes(self):
        report = self.report(
            [
                {"task_id": "retrieved", "tool": "web", "input": {"url": "known-fix/7"}},
                {"task_id": "retrieved", "tool": "edit", "input": {"path": "a.py"}},
                {"task_id": "retrieved", "passed": True},
                {"task_id": "derived", "tool": "read_file", "input": {"path": "b.py"}},
                {"task_id": "derived", "tool": "edit", "input": {"path": "b.py"}},
                {"task_id": "derived", "passed": True},
            ],
            markers=["known-fix/7"],
        )
        self.assertEqual(report["summary"]["passed_tasks"], 2)
        self.assertEqual(report["summary"]["confirmed_retrieval_passes"], 1)
        self.assertEqual(report["summary"]["retrieval_stripped_passes"], 1)
        self.assertEqual(report["summary"]["retrieval_share_of_passes"], 0.5)

    def test_shell_echo_write_prevents_late_reference_false_red(self):
        report = self.report(
            [
                {"tool": "shell", "input": {"command": "echo fixed > src/fix.py"}},
                {"tool": "web", "input": {"url": "https://github.com/acme/app/pull/42"}},
                {"event": "result", "passed": True},
            ],
            markers=["github.com/acme/app/pull/42"],
        )
        self.assertEqual(report["tasks"][0]["first_write_line"], 1)
        self.assertEqual(report["tasks"][0]["verdict"], "NO_SIGNAL_NOT_PROOF_OF_DERIVATION")

    def test_git_apply_is_a_write_boundary(self):
        report = self.report(
            [
                {"tool": "shell", "input": {"command": "git apply /tmp/fix.patch"}},
                {"tool": "web", "input": {"url": "https://github.com/acme/app/pull/42"}},
                {"event": "result", "passed": True},
            ],
            markers=["github.com/acme/app/pull/42"],
        )
        self.assertEqual(report["tasks"][0]["first_write_line"], 1)
        self.assertEqual(report["summary"]["confirmed_retrieval_passes"], 0)

    def test_marker_in_task_setup_is_not_agent_action(self):
        report = self.report(
            [
                {"event": "task_setup", "prompt": "Investigate github.com/acme/app/pull/42"},
                {"tool": "read_file", "input": {"path": "src/core.py"}},
                {"tool": "write_file", "input": {"path": "src/core.py"}},
                {"event": "result", "passed": True},
            ],
            markers=["github.com/acme/app/pull/42"],
        )
        self.assertEqual(report["tasks"][0]["verdict"], "NO_SIGNAL_NOT_PROOF_OF_DERIVATION")

    def test_marker_in_named_task_setup_is_not_agent_action(self):
        report = self.report(
            [
                {"name": "benchmark_task", "prompt": "See github.com/acme/app/pull/42"},
                {"name": "read_file", "input": {"path": "src/core.py"}},
                {"name": "write_file", "input": {"path": "src/core.py"}},
                {"event": "result", "passed": True},
            ],
            markers=["github.com/acme/app/pull/42"],
        )
        self.assertEqual(report["tasks"][0]["verdict"], "NO_SIGNAL_NOT_PROOF_OF_DERIVATION")

    def test_reference_without_detected_write_is_not_red(self):
        report = self.report(
            [
                {"tool": "web", "input": {"url": "https://github.com/acme/app/pull/42"}},
                {"event": "result", "passed": True},
            ],
            markers=["github.com/acme/app/pull/42"],
        )
        self.assertEqual(report["tasks"][0]["verdict"], "NOT_EVALUABLE_NO_WRITE_EVENT")
        self.assertEqual(report["summary"]["confirmed_retrieval_passes"], 0)

    def test_short_reference_marker_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least 8 characters"):
            self.report(
                [{"tool": "write_file", "input": {"path": "src/fix.py"}}],
                markers=["fix"],
            )

    def test_evidence_names_source_file(self):
        report = self.report(
            [
                {"tool": "web", "input": {"url": "https://github.com/acme/app/pull/42"}},
                {"tool": "write_file", "input": {"path": "src/fix.py"}},
                {"event": "result", "passed": True},
            ],
            markers=["github.com/acme/app/pull/42"],
        )
        evidence = report["tasks"][0]["confirmed_evidence"][0]
        self.assertTrue(evidence["file"].endswith("trajectory.jsonl"))

    def test_raw_patch_url_is_yellow_without_declared_marker(self):
        report = self.report(
            [
                {"tool": "web", "input": {"url": "https://raw.githubusercontent.com/acme/app/fix.patch"}},
                {"tool": "write_file", "input": {"path": "src/fix.py"}},
                {"event": "result", "passed": True},
            ]
        )
        self.assertEqual(report["tasks"][0]["verdict"], "YELLOW_SUSPICIOUS_PROVENANCE")

    def test_thread_started_prompt_cannot_trigger_red(self):
        report = self.report(
            [
                {"type": "thread_started", "prompt": "See github.com/acme/app/pull/42"},
                {"tool": "write_file", "input": {"path": "src/fix.py"}},
                {"event": "result", "passed": True},
            ],
            markers=["github.com/acme/app/pull/42"],
        )
        self.assertEqual(report["tasks"][0]["verdict"], "NO_SIGNAL_NOT_PROOF_OF_DERIVATION")

    def test_tool_named_task_setup_cannot_trigger_red(self):
        report = self.report(
            [
                {"tool": "task_setup", "input": {"prompt": "See github.com/acme/app/pull/42"}},
                {"tool": "write_file", "input": {"path": "src/fix.py"}},
                {"event": "result", "passed": True},
            ],
            markers=["github.com/acme/app/pull/42"],
        )
        self.assertEqual(report["tasks"][0]["verdict"], "NO_SIGNAL_NOT_PROOF_OF_DERIVATION")

    def test_tool_output_cannot_trigger_red(self):
        report = self.report(
            [
                {
                    "tool": "read_file",
                    "type": "tool_result",
                    "content": "CHANGELOG points to github.com/acme/app/pull/42",
                },
                {"tool": "write_file", "input": {"path": "src/fix.py"}},
                {"event": "result", "passed": True},
            ],
            markers=["github.com/acme/app/pull/42"],
        )
        self.assertEqual(report["tasks"][0]["verdict"], "NO_SIGNAL_NOT_PROOF_OF_DERIVATION")

    def test_top_level_shell_output_is_not_scanned(self):
        report = self.report(
            [
                {
                    "tool": "shell",
                    "command": "git status --short",
                    "output": "unrelated github.com/acme/app/pull/42",
                },
                {"tool": "write_file", "input": {"path": "src/fix.py"}},
                {"event": "result", "passed": True},
            ],
            markers=["github.com/acme/app/pull/42"],
        )
        self.assertEqual(report["tasks"][0]["verdict"], "NO_SIGNAL_NOT_PROOF_OF_DERIVATION")

    def test_top_level_web_url_can_confirm_declared_reference(self):
        report = self.report(
            [
                {"tool": "web", "url": "https://github.com/acme/app/pull/42"},
                {"tool": "write_file", "input": {"path": "src/fix.py"}},
                {"event": "result", "passed": True},
            ],
            markers=["github.com/acme/app/pull/42"],
        )
        self.assertEqual(report["tasks"][0]["verdict"], "RED_CONFIRMED_RETRIEVAL_BEFORE_DERIVATION")

    def test_composite_terminal_tool_sets_write_boundary(self):
        report = self.report(
            [
                {
                    "tool": "run_terminal_cmd",
                    "input": {"command": "sed -i 's/old/new/' src/core.py"},
                },
                {"tool": "web", "input": {"url": "https://github.com/acme/app/pull/42"}},
                {"tool": "write_file", "input": {"path": "src/fix.py"}},
                {"event": "result", "passed": True},
            ],
            markers=["github.com/acme/app/pull/42"],
        )
        self.assertEqual(report["tasks"][0]["first_write_line"], 1)
        self.assertEqual(report["tasks"][0]["verdict"], "NO_SIGNAL_NOT_PROOF_OF_DERIVATION")

    def test_user_command_is_not_agent_action(self):
        report = self.report(
            [
                {
                    "event": "user_command",
                    "input": {"text": "Inspect github.com/acme/app/pull/42"},
                },
                {"tool": "write_file", "input": {"path": "src/fix.py"}},
                {"event": "result", "passed": True},
            ],
            markers=["github.com/acme/app/pull/42"],
        )
        self.assertEqual(report["tasks"][0]["verdict"], "NO_SIGNAL_NOT_PROOF_OF_DERIVATION")

    def test_denied_approval_request_is_not_access(self):
        report = self.report(
            [
                {
                    "type": "command_approval_request",
                    "command": "curl https://github.com/acme/app/pull/42.diff",
                    "status": "denied",
                },
                {"tool": "write_file", "input": {"path": "src/fix.py"}},
                {"event": "result", "passed": True},
            ],
            markers=["github.com/acme/app/pull/42"],
        )
        self.assertEqual(report["tasks"][0]["verdict"], "NO_SIGNAL_NOT_PROOF_OF_DERIVATION")


if __name__ == "__main__":
    unittest.main()
