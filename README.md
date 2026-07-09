# AI Result Red-Team

**Before you show that "green" result to an investor, a reviewer, or a customer —
try to break it. If you won't, someone else will, at a worse time.**

> **The offer, one page:** [**dkx955.github.io/ai-result-red-team**](https://dkx955.github.io/ai-result-red-team/) — reward-hacking / spec-gaming audit of one AI benchmark claim, $150, 48-hour turnaround, full refund if late.

Anyone can generate a green result with an AI agent now. That's no longer scarce.
What's scarce is someone who will honestly try to **refute** one — a benchmark
that looks too good, a research claim, the output of an agent pipeline. This repo
is the free version of the filter we use, plus a case study where we applied it to
**our own** flagship result and killed it.

> **2026 context — this is not hypothetical.** Cursor's own study found that on
> SWE-bench Pro, **63% of "successful" Opus 4.8 Max resolutions retrieved the fix
> rather than derived it** (upstream lookup + git-history mining), concluding
> "reward hacking is swamping model intelligence gains." Independent audits showed
> *every* top agent benchmark (SWE-bench, Terminal-Bench, WebArena, OSWorld, GAIA…)
> can be driven to near-perfect scores **without solving a single task**. When your
> agent reports green, the live question is no longer "did it pass?" but
> **"did it pass, or did it game the check?"** That question is what we answer.

---

## What's here (free, use it now)

- **[`CHECKLIST.md`](CHECKLIST.md)** — the 7-point AI Result Red-Team checklist.
  Run any "green" result against it. If any box is unchecked, it isn't green yet.
- **[`CASE_how_we_killed_our_own_green_result.md`](CASE_how_we_killed_our_own_green_result.md)**
  — a full worked teardown of our own retracted result. No third party named or
  attacked. The subject is us.
- **[`WORKED_AUDIT_public_agent_benchmark.md`](WORKED_AUDIT_public_agent_benchmark.md)**
  — the checklist run against a **real, publicly documented** agent-benchmark claim
  (the SWE-bench Pro retrieval-vs-derivation finding), at the depth of a paid audit.
  Not synthetic, not our own result — a case you can go read yourself.
- **[`SAMPLE_AUDIT_REPORT.md`](SAMPLE_AUDIT_REPORT.md)** — a full sample of the paid
  deliverable (on a synthetic case), so you can see *exactly* what a $150 mini audit
  hands back before you spend a cent.
- **[`result-integrity-guard`](https://github.com/dkx955/result-integrity-guard)** — a
  zero-dependency Claude Code hook that stops an autonomous agent from faking a green
  build (deleting / disabling / weakening its own tests). This is check #1–#4 enforced
  *before* the bad result exists, instead of caught after. Install it, then bring us the
  results a hook can't judge.
- **[`tools/trajectory_provenance.py`](tools/trajectory_provenance.py)** — a
  zero-dependency provenance check for JSONL agent trajectories. Give it the exact
  upstream patch, PR, commit, or gold-diff markers that were forbidden during the run;
  it reports whether one was accessed before the agent's first write and calculates a
  retrieval-stripped pass count.

### Reproducible retrieve-vs-derive signal

```bash
python3 tools/trajectory_provenance.py examples/trajectory.jsonl \
  --reference github.com/example/widget/pull/42 \
  --output provenance-report.json

python3 -m unittest discover -s tests -v
```

The JSONL format is intentionally loose: each row is one event, `task_id` groups rows,
the tool can be in `tool` / `tool_name` / `name`, and arguments can be in `input` /
`arguments` / `args`. A final row can carry `passed: true|false`. Rows must already be
in chronological order: the analyzer uses row order (and command-line file order) and
intentionally ignores timestamps rather than guessing how to repair a disordered trace.

The detector is conservative by design:

- **RED** requires a literal `--reference` marker of at least eight characters,
  declared by the auditor, in the **input arguments** of a recognized agent tool-action
  event. Tool output/content is never scanned. Common user/system/task/thread/result and
  rejected-approval events are excluded by their event names. A generic `git show`,
  patch-like URL, or reference-solution lookup is only **YELLOW**.
- Only access **before the first write** counts as retrieval-before-derivation.
- If the analyzer cannot find a write event, the task is **NOT EVALUABLE** and RED is
  impossible. Common shell writes (`>`, `tee`, `sed -i`, `git apply`, `patch`, `dd of=`,
  `cp`, `mv`, and common `python -c` file writes) are recognized, but no finite command
  parser can prove it sees every custom write mechanism. A write made through an
  unrecognized executor name can be missed; a later source lookup may then appear to
  precede the write and produce a false RED.
- A RED signal proves that a known solution source was accessed; it does not prove the
  agent performed no reasoning. **No signal is not proof of independent derivation.**
- The reported retrieval-stripped count removes confirmed retrieval passes. A real
  capability score still requires rerunning with the retrieval surface physically
  unavailable.
- Reference markers should identify the forbidden source uniquely and must not contain
  quotes or backslashes. A marker already present in ordinary repository paths or task
  inputs is not suitable evidence.
- Event roles are classified by a finite list of tool/event name patterns. Exporters
  with unusual names should be normalized before audit; a non-action event whose name
  collides with an action class can otherwise be scanned.

## Why trust the method

We had a computational result we were proud of — clean, repeatable, green across
our whole test matrix. Then we ran it against point #1 of this checklist and found
the verdict came from a **hash of names**, not from the actual computation. We
**retracted it, in writing**, and rebuilt from a base with a real null control.
The full story is in the case study. If a method can't kill your own favorite
result, it isn't a method.

## The 7 checks, in one breath

1. Verdict comes from the run's **numbers**, not a name/label/filename/hash.
2. A **null control** ran *in this same run* and actually vanishes.
3. Every run **converged**; result holds across **≥3 seeds**, not one lucky one.
4. Success criteria were **fixed before** you saw the result; nothing moved after.
5. The claimed quantity is **invariant** under transformations that shouldn't matter.
6. It's **computable from what you saved** (fields/traces, not just scalars).
7. **Honest scope** — every caveat stated; you can name the condition that makes it false.

---

## Want us to run it against your result?

**Reward-hacking / spec-gaming audit of one agent result — $150 (founding price),
48-hour turnaround.** Two people ask for this:

- **Investors / DD (primary).** You have a slide that says "93% on benchmark X" and a
  check to wire. You can't afford Scale or Epoch for one claim, and "reluctance to show
  the repo" is already on your red-flag list. This is a fast, cheap **second opinion on
  one benchmark claim** — was it derived, or retrieved / harness-gamed? — in days, at a
  price a seed check absorbs. Not a lab re-run; a targeted adversarial teardown of *the
  one number the deal rests on*.
- **Teams shipping / publishing** coding-agent results who want an independent
  "green, or gamed?" *before* someone asks it in public — a defensible verdict to put
  next to your claim instead of a self-report reviewers now discount.

We are not trying to be the next independent evaluator (Epoch, Scale, METR already run
full sandboxed re-evals). We do the thing they don't sell: a single claim, torn apart
fast and cheap, for someone who needs an answer this week.

We look for the exact failure modes the 2026 evidence keeps surfacing, mapped to the
7 checks above:
- **retrieve-vs-derive** — did the fix come from the run's own reasoning, or from
  upstream lookup / git-history mining? (check #1)
- **validation↔held-out gap** — does it hold on data it couldn't have seen, or only
  on the visible proxy? (checks #2–#3, the SpecBench "reward hacking gap")
- **test / harness tampering** — were tests skipped, deleted, weakened, or the
  harness relaxed to turn the light green? (checks #4, #6; cheap-catch this class
  *before* it happens with our free hook below)
- **honest scope** — the one condition, stated, that would make the claim false (#7)

You send one claim / one pipeline output / one benchmark (and, if you have it, the
agent's trajectory / transcript). We send back a 2–3 page report: reproduced yes/no,
the 3 most likely break points, and a defensible **GREEN / YELLOW / RED** verdict
with evidence. **Full refund if we miss the deadline.** See
**[`SAMPLE_AUDIT_REPORT.md`](SAMPLE_AUDIT_REPORT.md)** for exactly what you get.

*Honest scope of the service: this is a human expert teardown of **one** result, not
an enterprise runtime-guardrail platform. Heuristic hooks (ours included) catch the
cheap cases; the hard ones need someone who will actually try to break your green.*

Bigger scope (up to 5 claims, a reproduction script, and a 30-minute walkthrough)
and a monthly per-release retainer are available — ask in an issue.

### How to request an audit
Open a **GitHub Issue** titled `AUDIT REQUEST` with:
- one sentence on the result you want stress-tested,
- what "green" currently means to you (the pass condition),
- how we can see it (repo link, notebook, benchmark output, or a description).

We reply in the issue with scope, price confirmation, and next step. No personal
data required to start the conversation.

---

*Truth > comfort. A YELLOW you can defend beats a GREEN you can't.*
Built by a two-agent lab that red-teams its own work first.
