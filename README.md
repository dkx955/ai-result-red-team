# AI Result Red-Team

**Before you show that "green" result to an investor, a reviewer, or a customer —
try to break it. If you won't, someone else will, at a worse time.**

Anyone can generate a green result with an AI agent now. That's no longer scarce.
What's scarce is someone who will honestly try to **refute** one — a benchmark
that looks too good, a research claim, the output of an agent pipeline. This repo
is the free version of the filter we use, plus a case study where we applied it to
**our own** flagship result and killed it.

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

**Mini red-team audit — $150 (founding price), 48-hour turnaround.**
You send one claim / one pipeline output / one benchmark. We send back a 2–3 page
report: reproduced yes/no, the 3 most likely break points, and a defensible
**GREEN / YELLOW / RED** verdict with evidence. **Full refund if we miss the
deadline.** See **[`SAMPLE_AUDIT_REPORT.md`](SAMPLE_AUDIT_REPORT.md)** for exactly
what you get.

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
