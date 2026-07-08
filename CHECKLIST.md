# The AI Result Red-Team Checklist (free)

*Before you show that "green" result to an investor, a reviewer, or a customer —
run it against this list. If any answer is "no", your result is not green yet.*

Made by operators who once retracted their **own** flagship result after it passed
every surface check — because the verdict came from a hash of names, not from the
actual computation. This list is the filter we now apply to everything. The full
story is in [`CASE_how_we_killed_our_own_green_result.md`](CASE_how_we_killed_our_own_green_result.md).

---

## 1. Provenance of the verdict
- [ ] The pass/fail came from the **numbers of the run** (measured outputs), not
      from a name, a label, a filename, or a hash of inputs.
- [ ] If you deleted the "expected answer" and re-derived it blind, you'd get the
      same verdict.

## 2. The null control actually ran
- [ ] There is a control condition where the effect **must vanish** (feature off,
      seed shuffled, input zeroed) — and it was computed **in this same run**.
- [ ] The control genuinely vanishes. (A control you didn't run ≠ a control.)

## 3. Convergence / stability
- [ ] Every run reached a stable state (loss/energy/error below your preregistered
      threshold). Unconverged runs are excluded or flagged, not averaged in.
- [ ] The result holds across ≥3 independent seeds / splits, not one lucky one.

## 4. No moving goalposts
- [ ] Success criteria were fixed **before** you saw the result (write them down).
- [ ] No threshold, metric, or filter was adjusted *after* seeing the outcome.
- [ ] If you added a parameter and it got "greener" — you can show it's not just a
      crutch fitted to the answer.

## 5. Invariance / gauge check
- [ ] The claimed quantity is invariant under transformations that shouldn't change
      it (units, ordering, equivalent representations, redundant symmetry).
- [ ] You're not measuring an artifact of your representation instead of the object.

## 6. It's computable from what you saved
- [ ] You saved the actual fields/arrays/traces needed to *reproduce the metric* —
      not only the scalar summary. (A scalar can't rebuild a profile or a localization.)
- [ ] Resolution in space/time is fine enough for the discriminator you claim.

## 7. Honest scope
- [ ] Every caveat is stated with the claim: sample size, regime, single-vs-many,
      what was NOT tested.
- [ ] You can name the exact condition under which this result would be **false**.

---

### Verdict
- **GREEN** — all boxes checked, controls ran, converged, criteria pre-registered.
- **YELLOW** — real signal but a box is unchecked (unconverged runs, one seed, scope).
- **RED** — verdict came from a name/hash, control missing, or goalposts moved.

*Truth > comfort. A YELLOW you can defend beats a GREEN you can't.*

---

Want us to run this against your pipeline and hand you the report?
**Mini red-team audit — one claim, 2–3 page report, 48h, $150 (founding price).**
Full refund if we miss the deadline. Open a GitHub Issue titled `AUDIT REQUEST` —
see the [README](README.md) for what to include.
