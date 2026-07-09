#!/usr/bin/env python3
"""Find pre-declared solution sources read before an agent's first write.

This is a deliberately conservative provenance signal, not a mind reader. A RED
finding requires a caller-supplied reference marker. Generic history or PR access
is only YELLOW, and no finding is never treated as proof of derivation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


EventRecord = tuple[str, int, dict[str, Any]]

WRITE_TOOL_RE = re.compile(
    r"(?:^|[_./-])(apply[_-]?patch|edit|write|replace|create[_-]?file|notebook[_-]?edit)(?:$|[_./-])",
    re.IGNORECASE,
)
SHELL_WRITE_RE = re.compile(
    r"(?:^|[;&|]\s*)(?:"
    r"(?:cat|echo|printf)\b[^;&|]*>|"
    r"tee(?:\s+-a)?\s+|"
    r"sed\s+-i(?:\s|$)|"
    r"perl\s+-[pi]+(?:\s|$)|"
    r"git\s+apply(?:\s|$)|"
    r"patch(?:\s|$)|"
    r"dd\b[^;&|]*\bof=|"
    r"(?:cp|mv|install)\b|"
    r"python(?:3)?\b[^;&|]*\s-c\s+[^;&|]*(?:write_text|write_bytes|open\s*\([^)]*,\s*['\"](?:w|a|x))"
    r")",
    re.IGNORECASE,
)
SUSPICIOUS_RE = re.compile(
    r"(?:"
    r"\bgit\s+(?:show|blame|log\b[^\n]*(?:--patch|-p\b))|"
    r"https?://[^\s\"']+/(?:commit|pull|merge_requests?)/[^\s\"']+|"
    r"https?://[^\s\"']+\.(?:patch|diff)(?:\?[^\s\"']*)?|"
    r"\b(?:gold|golden|reference|expected)[ _-](?:patch|diff|solution)\b"
    r")",
    re.IGNORECASE,
)
ACTION_TOOL_RE = re.compile(
    r"(?:^|[_./-])(?:shell|bash|terminal|exec|exec[_-]?command|command|"
    r"read|read[_-]?file|open|fetch|web|web[_-]?search|browser|curl|git|"
    r"apply[_-]?patch|edit|write|replace|create[_-]?file|notebook[_-]?edit)"
    r"(?:$|[_./-])",
    re.IGNORECASE,
)
SHELL_TOOL_RE = re.compile(
    r"(?:^|[_./-])(?:shell|bash|terminal|exec|command|cmd)(?:$|[_./-])",
    re.IGNORECASE,
)
NON_ACTION_EVENT_RE = re.compile(
    r"(?:^|[_./-])(?:user|system|prompt|thread|task|setup|approval|request|result|output)"
    r"(?:$|[_./-])",
    re.IGNORECASE,
)
REJECTED_STATUSES = {"denied", "rejected", "canceled", "cancelled"}
SCAN_TOP_LEVEL_KEYS = ("command", "cmd", "script", "path", "url", "query", "patch", "file", "target")


def canonical_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def event_tool(event: dict[str, Any]) -> str:
    for key in ("tool", "tool_name", "name", "event", "type"):
        value = event.get(key)
        if isinstance(value, str):
            return value
    return ""


def event_payload(event: dict[str, Any]) -> Any:
    for key in ("input", "arguments", "args", "parameters"):
        if key in event:
            return event[key]
    return event


def is_agent_action_event(event: dict[str, Any]) -> bool:
    for key in ("event", "type"):
        value = event.get(key)
        if isinstance(value, str) and NON_ACTION_EVENT_RE.search(value):
            return False
    for key in ("tool", "tool_name", "name", "event", "type"):
        value = event.get(key)
        if isinstance(value, str) and ACTION_TOOL_RE.search(value):
            return True
    return False


def event_was_rejected(event: dict[str, Any]) -> bool:
    status = event.get("status")
    return isinstance(status, str) and status.strip().casefold() in REJECTED_STATUSES


def event_scan_input(event: dict[str, Any]) -> Any | None:
    for key in ("input", "arguments", "args", "parameters"):
        if key in event:
            return event[key]
    selected = {key: event[key] for key in SCAN_TOP_LEVEL_KEYS if key in event}
    return selected or None


def shell_command(event: dict[str, Any]) -> str:
    payload = event_payload(event)
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        for key in ("command", "cmd", "script"):
            value = payload.get(key)
            if isinstance(value, str):
                return value
    return ""


def is_write_event(event: dict[str, Any]) -> bool:
    if event_was_rejected(event):
        return False
    tool = event_tool(event)
    if WRITE_TOOL_RE.search(tool):
        return True

    if SHELL_TOOL_RE.search(tool):
        return bool(SHELL_WRITE_RE.search(shell_command(event)))
    return False


def task_id(event: dict[str, Any], default: str) -> str:
    for key in ("task_id", "task", "episode_id", "run_id"):
        value = event.get(key)
        if value is not None:
            return str(value)
    return default


def result_passed(events: list[EventRecord]) -> bool | None:
    for _, _, event in reversed(events):
        if isinstance(event.get("passed"), bool):
            return event["passed"]
        result = event.get("result")
        if isinstance(result, dict) and isinstance(result.get("passed"), bool):
            return result["passed"]
        status = event.get("status")
        if isinstance(status, str):
            normalized = status.strip().lower()
            if normalized in {"passed", "pass", "success", "green"}:
                return True
            if normalized in {"failed", "fail", "error", "red"}:
                return False
    return None


def evidence_item(
    source_file: str,
    line_number: int,
    event: dict[str, Any],
    kind: str,
    marker: str | None = None,
) -> dict[str, Any]:
    text = canonical_text(event)
    item: dict[str, Any] = {
        "file": source_file,
        "line": line_number,
        "kind": kind,
        "tool": event_tool(event) or None,
        "excerpt": text[:500],
    }
    if marker is not None:
        item["reference_marker"] = marker
    return item


def analyze_task(
    identifier: str,
    events: list[EventRecord],
    reference_markers: list[str],
) -> dict[str, Any]:
    first_write_position: int | None = None
    first_write_line: int | None = None
    for position, (_, line_number, event) in enumerate(events):
        if is_write_event(event):
            first_write_position = position
            first_write_line = line_number
            break

    pre_write = events if first_write_position is None else events[:first_write_position]
    confirmed: list[dict[str, Any]] = []
    suspicious: list[dict[str, Any]] = []

    for source_file, line_number, event in pre_write:
        if event_was_rejected(event) or not is_agent_action_event(event):
            continue
        scan_input = event_scan_input(event)
        if scan_input is None:
            continue
        text = canonical_text(scan_input)
        lowered = text.casefold()
        matched = [marker for marker in reference_markers if marker.casefold() in lowered]
        if matched:
            confirmed.extend(
                evidence_item(
                    source_file,
                    line_number,
                    event,
                    (
                        "declared_reference_before_write"
                        if first_write_position is not None
                        else "declared_reference_seen_without_write_boundary"
                    ),
                    marker,
                )
                for marker in matched
            )
        elif SUSPICIOUS_RE.search(text):
            suspicious.append(
                evidence_item(
                    source_file,
                    line_number,
                    event,
                    "possible_solution_lookup_before_write",
                )
            )

    if first_write_position is None:
        verdict = "NOT_EVALUABLE_NO_WRITE_EVENT"
    elif confirmed:
        verdict = "RED_CONFIRMED_RETRIEVAL_BEFORE_DERIVATION"
    elif suspicious:
        verdict = "YELLOW_SUSPICIOUS_PROVENANCE"
    else:
        verdict = "NO_SIGNAL_NOT_PROOF_OF_DERIVATION"

    return {
        "task_id": identifier,
        "passed": result_passed(events),
        "event_count": len(events),
        "first_write_line": first_write_line,
        "verdict": verdict,
        "confirmed_evidence": confirmed,
        "suspicious_evidence": suspicious,
    }


def read_jsonl(path: Path) -> list[EventRecord]:
    events: list[EventRecord] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: every JSONL row must be an object")
            events.append((str(path), line_number, value))
    return events


def load_reference_markers(inline: list[str], files: list[Path]) -> list[str]:
    markers = [value.strip() for value in inline if value.strip()]
    for path in files:
        for raw in path.read_text(encoding="utf-8").splitlines():
            value = raw.strip()
            if value and not value.startswith("#"):
                markers.append(value)
    markers = sorted(set(markers), key=str.casefold)
    too_short = [marker for marker in markers if len(marker) < 8]
    if too_short:
        rendered = ", ".join(repr(marker) for marker in too_short)
        raise ValueError(f"reference markers must contain at least 8 characters: {rendered}")
    return markers


def build_report(paths: list[Path], markers: list[str]) -> dict[str, Any]:
    too_short = [marker for marker in markers if len(marker) < 8]
    if too_short:
        raise ValueError("reference markers must contain at least 8 characters")
    grouped: dict[str, list[EventRecord]] = defaultdict(list)
    for path in paths:
        default_task = path.stem
        for source_file, line_number, event in read_jsonl(path):
            identifier = task_id(event, default_task)
            grouped[identifier].append((source_file, line_number, event))

    tasks = [analyze_task(key, grouped[key], markers) for key in sorted(grouped)]
    passed = [task for task in tasks if task["passed"] is True]
    confirmed_passes = [
        task for task in passed if task["verdict"] == "RED_CONFIRMED_RETRIEVAL_BEFORE_DERIVATION"
    ]
    suspicious_passes = [
        task for task in passed if task["verdict"] == "YELLOW_SUSPICIOUS_PROVENANCE"
    ]

    return {
        "schema_version": 1,
        "method": "declared-reference-before-first-write",
        "scope_warning": (
            "A confirmed marker is evidence of retrieval, not proof that no reasoning occurred. "
            "No signal is not proof of derivation."
        ),
        "ordering_assumption": (
            "Events are analyzed in JSONL row order and input-file argument order; timestamps are ignored."
        ),
        "reference_marker_count": len(markers),
        "summary": {
            "tasks": len(tasks),
            "passed_tasks": len(passed),
            "confirmed_retrieval_passes": len(confirmed_passes),
            "suspicious_provenance_passes": len(suspicious_passes),
            "retrieval_share_of_passes": (
                len(confirmed_passes) / len(passed) if passed else None
            ),
            "retrieval_stripped_passes": len(passed) - len(confirmed_passes),
        },
        "tasks": tasks,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Flag declared solution sources accessed before an agent's first write."
    )
    parser.add_argument("trajectory", nargs="+", type=Path, help="JSONL trajectory file(s)")
    parser.add_argument(
        "--reference",
        action="append",
        default=[],
        help="Literal marker for a known solution source; repeat as needed",
    )
    parser.add_argument(
        "--reference-file",
        action="append",
        default=[],
        type=Path,
        help="Text file with one literal reference marker per line",
    )
    parser.add_argument("--output", type=Path, help="Write JSON report here instead of stdout")
    parser.add_argument(
        "--fail-on-confirmed",
        action="store_true",
        help="Exit 1 when a passed task has confirmed retrieval evidence",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        markers = load_reference_markers(args.reference, args.reference_file)
        report = build_report(args.trajectory, markers)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)

    if args.fail_on_confirmed and report["summary"]["confirmed_retrieval_passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
