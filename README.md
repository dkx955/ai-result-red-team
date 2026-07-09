# AI Result Red-Team

**Before you show that "green" result to an investor, a reviewer, or a customer —
try to break it. If you won't, someone else will, at a worse time.**

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
- **[`SAMPLE_AUDIT_REPORT.md`](SAMPLE_AUDIT_REPORT.md)** — a full sample of the paid
  deliverable (on a synthetic case), so you can see *exactly* what a $150 mini audit
  hands back before you spend a cent.
- **[`result-integrity-guard`](https://github.com/dkx955/result-integrity-guard)** — a
  zero-dependency Claude Code hook that stops an autonomous agent from faking a green
  build (deleting / disabling / weakening its own tests). This is check #1–#4 enforced
  *before* the bad result exists, instead of caught after. Install it, then bring us the
  results a hook can't judge.

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
48-hour turnaround.** For teams shipping or publishing coding-agent results who need
an independent "green, or gamed?" before someone else asks it in public.

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
