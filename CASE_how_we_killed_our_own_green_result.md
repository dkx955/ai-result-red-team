# Teardown #1 — how we red-teamed our own flagship result and killed it

*A worked example of the checklist in this repo, applied to our own work. No
third party is named or attacked. The subject is us. That is the point: if the
method can't kill your own favorite result, it isn't a method.*

---

## The result we were proud of

We had a computational-physics line (internal codename **BION / C8**, hypothesis
stages H0–H7b). It produced a clean, repeatable **green verdict**: the object we
were hunting appeared to be there, run after run, across our test matrix. Every
surface check passed. We were one write-up away from calling it a discovery.

## Where the checklist bit

We ran the result against **item #1 — provenance of the verdict**:

> The pass/fail must come from the numbers of the run, not from a name, a label,
> a filename, or a hash of inputs.

It did not.

The "verdict" in H0–H7b was ultimately driven by a `sha256` over **names and a
closed-form formula** (`tanh`/`sin`/`cos`), not by integrating the actual field.
In plain terms: it was a **table generator dressed as a simulation**. The green
came from the label, not from the physics. When you delete the expected answer
and try to re-derive it blind from the saved state, you can't — because the
state was never the thing being measured.

That is a textbook **RED** under our own rule: *the verdict came from a
name/hash, not from the computation.*

## What we did about it

We **retracted the entire BION/C8 H0–H7b line as physical evidence.** Not
quietly — in writing, as the current honest state of the project:

- The hypothesis itself is **left open, not declared dead.** Killing the *evidence*
  is not the same as killing the *idea*. Overclaiming a kill is the same sin as
  overclaiming a discovery, just inverted.
- We rebuilt from the only honest base: a line where the verdict comes from
  integrating the field and checking a **null control** (with the coupling turned
  off, the effect must annihilate — and it does).
- We wrote a standing filter (we call it the **Nexus filter**) that every result
  now has to pass *before* it can be called green. This repo's checklist is the
  public version of it.

## The five questions that would have caught it earlier

Applied to any "green" result, ours included:

1. **Did the verdict come from the run's numbers** (measured outputs) — not a
   name, label, filename, or hash of inputs?
2. **Did the null control actually run in this same run, and does it vanish?**
   (A control you didn't compute is not a control.)
3. **Did every run converge** to a stable state below a pre-registered threshold,
   across ≥3 independent seeds — not one lucky one?
4. **Were the success criteria fixed before you saw the result** — and did no
   threshold, metric, or filter move afterward?
5. **Is the claimed quantity invariant** under transformations that shouldn't
   change it (units, ordering, gauge, equivalent representations)?

If any answer is "no," the result is not green yet. Ours failed #1 outright, so
the rest didn't even get a chance to save it.

## Two rules we now enforce, because this cost us

- **Save the fields, not just the scalars.** A scalar summary (an energy, a count,
  a spectrum) *cannot* rebuild a profile, verify localization, or support a gauge
  test. On one decisive test we had only scalars saved — and the test became
  literally uncomputable after the fact. A whole run, wasted, because the array we
  needed was never written to disk. Now: snapshots of the actual field are saved
  at every pre-registered moment, or the run doesn't count.
- **Pre-register the acceptance criteria in a file, before the run.** After the
  run, the criteria do not change. If you *want* to change them, that wish is a
  signal of researcher degrees of freedom — you log it separately and explain it,
  you don't silently move the line.

## Why we publish this against ourselves

Anyone can generate a green result with an agent now. That is no longer scarce.
What's scarce is someone who will **honestly try to break it** — including their
own. This teardown is the credential. We killed the result we most wanted to
keep, on the record, using exactly the checklist in this repo.

If you have a "green" result — a benchmark, a research claim, an AI-agent
pipeline output — and you'd rather find the crack yourself than have an investor,
a reviewer, or a customer find it for you, that's the service. See the README.
