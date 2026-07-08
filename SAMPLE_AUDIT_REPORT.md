# Sample Audit Report — what a Mini Red-Team Audit actually looks like

> **This is a sample.** The subject below is a **synthetic** case built to show the
> exact format and depth you get for a $150 mini audit. No real company, product,
> or person is described. Your real report follows this same structure, on your
> result, with your evidence.

---

**Audit ID:** SAMPLE-0001
**Subject:** One benchmark claim (synthetic)
**Turnaround:** delivered within 48h of intake
**Scope purchased:** Mini — 1 claim, reproduce yes/no, top-3 break points, one verdict

---

## 0. The claim as received

> *"Our support-agent RAG pipeline answers customer tickets at **94% accuracy**.
> We're putting this number in the seed deck and on the pricing page."*

Pass condition given to us by the client (their words):
> *"Accuracy ≥ 90% on our 500-ticket eval set."*

What we were given to work with: the eval script, the 500-ticket set, the retrieval
index build script, and the raw model outputs for the reported run.

---

## 1. Reproduced? — **Partially (number reproduces, meaning does not)**

We re-ran the client's own script unchanged. It reprinted **94.2%**. So the number
is not fabricated — it comes out of the script.

But "reproduced" in a red-team sense means: *does the number mean what the claim
says it means?* Here it does not, for three reasons below. **The 94% is real as a
script output and misleading as a product claim.**

---

## 2. The three most likely break points (ranked by how much they move the number)

### BREAK #1 — Train/eval contamination in the retrieval index *(fatal to the claim)*
The retrieval index was built from the **full** knowledge base, and 137 of the 500
eval tickets have their **resolved answer text present verbatim** in an indexed
document. On those 137, the pipeline retrieves the answer and paraphrases it —
accuracy on that slice is 99%. On the 363 genuinely unseen tickets, accuracy is
**81.3%**.

- Checklist point failed: **#2 (no honest null)** and **#5 (measuring an artifact
  of the setup, not the capability)**.
- Effect on the number: the headline 94% is inflated by ~13 points of leakage.
  The defensible number for *unseen* tickets is **~81%**, below the client's own
  90% bar.

**How we found it:** hashed every eval answer, searched the index corpus for
near-duplicates (>0.9 cosine + exact n-gram overlap), and split the score by
"answer-in-index" vs "not." The split is the whole story.

### BREAK #2 — Single run, no seed variance *(unknown risk)*
The 94.2% is one run. Retrieval top-k ordering and the model's temperature > 0 make
this stochastic. We re-ran the *unseen* slice across 5 seeds: **78.9% – 83.4%**,
mean 81.1%, and one seed dipped to 78.9%.

- Checklist point failed: **#3 (≥3 seeds)**.
- Effect: even the honest 81% has a ±2.5 pt spread. A pricing-page number needs a
  reported interval, not a point estimate.

### BREAK #3 — "Accuracy" is graded by the same model family *(soft)*
Correctness was judged by an LLM grader from the same model family as the answerer,
with a lenient rubric ("is the answer roughly right?"). On a 40-ticket hand-check,
the grader was **11% too generous** vs. two human raters (it passed answers that
were confidently wrong on policy details).

- Checklist point failed: **#1 (verdict provenance)** — the pass came partly from a
  self-friendly grader, not a ground truth.
- Effect: subtract a few more points, or re-grade with a held-out rubric + spot
  human check. We did not fully quantify this in a mini audit; flagged for a full audit.

---

## 3. Verdict

# 🔴 RED — as stated ("94% accuracy")
The headline number cannot go on the pricing page. It is inflated by eval
contamination (#2, #5), rests on a single seed (#3), and leans on a self-friendly
grader (#1).

There **is** a real, defensible result underneath:

# 🟡 YELLOW — "~81% on unseen tickets (5-seed mean, self-graded — human check pending)"
That sentence you *can* defend to an investor who does diligence. It is lower, and
it is real. A YELLOW you can defend beats a GREEN you can't.

---

## 4. What to do before you claim green (concrete, ordered)

1. **De-leak the eval.** Exclude eval-answer text from the retrieval corpus, or hold
   out the 500 tickets' source docs. Re-score. This is the one that matters.
2. **Report an interval, not a point.** ≥5 seeds, publish mean ± spread.
3. **Grade with a held-out rubric** and a ≥40-item human spot check; report grader
   agreement.
4. Then re-run this checklist. If all boxes check, *that* number is a green you own.

Estimated effort for the client: ~1 day of engineering. Cheaper now than after an
investor's technical advisor finds BREAK #1 in the data room.

---

## 5. What was NOT tested (honest scope of a mini audit)
- Only the one accuracy claim; latency, cost, and safety claims were out of scope.
- BREAK #3 was flagged, not fully quantified (needs the full-audit human panel).
- We did not audit the 500-ticket set for representativeness vs. live traffic.

---

*This is the deliverable. Yours will look like this, on your result.*
**Mini red-team audit — $150 (founding price), 48h, full refund if we miss the
deadline.** Open a GitHub Issue titled `AUDIT REQUEST` — see the
[README](README.md) for what to include.
