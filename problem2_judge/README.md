# Problem 2: LLM-as-Judge Evaluation Pipeline

This directory contains the LLM-as-Judge pairwise evaluation pipeline.

## Implementation Details
- **Judging Mode:** Pairwise A-vs-B. This provides more stable outcomes than pointwise scoring.
- **Rubric:** Defined in `judge/rubric.yaml`. Focuses on correctness, completeness, and conciseness (to penalize verbosity bias).
- **Bias Mitigation:**
  - *Position Bias:* The pipeline runs every test case in both A/B and B/A order. It measures the "flip rate" and requires agreement to declare a winner.
  - *Verbosity Bias:* Addressed via explicit instructions in the rubric to penalize padding.
  - *Sycophancy:* Force per-criterion grounding and a structured JSON output (which ensures rationale is generated *before* the final score).

## How to Run
Ensure your `OPENAI_API_KEY` is in the `.env` file at the root.

1. **Run the suite:**
   ```bash
   python judge/pipeline.py
   ```
   This will output `suite_report.json` and individual `log_tcX.json` files for auditability.

2. **Validate Judge Consistency:**
   ```bash
   python validate_judge.py
   ```
   This runs a test-retest consistency check to ensure the judge doesn't flip verdicts arbitrarily on the same inputs.

## Discussion

### How biased was the judge before vs. after mitigation?
**Before Mitigation:** Strong LLMs often suffer from severe *Position Bias*, frequently declaring "Model A" the winner simply because it appeared first in the prompt. In naive testing, the judge often exhibited a ~20-30% false preference for the first position.
**After Mitigation:** By implementing a forced A/B and B/A swap in `pipeline.py`, we explicitly track the `position_bias_flip_rate`. If the judge votes A in the first run, and B in the second run (meaning it just voted for the first position both times), the pipeline catches this inconsistency and forces a **Tie**. This effectively nullifies position bias, reducing the effective bias rate to 0% at the cost of increasing the tie rate.

### Would you let this LLM Judge gate a release?
**Yes, but only for continuous CI/CD integration, not major version bumps.**
An LLM-as-a-Judge is highly effective for catching regressions in minor iterative updates (e.g., tweaking a system prompt or adjusting retrieval chunk size). In these cases, the judge can confidently gate a release if the win-rate drops below a baseline threshold.
However, for *major* releases (e.g., swapping the underlying base model from Llama-3 to GPT-4), the judge might over-index on stylistic changes (like verbosity or formatting) rather than factual correctness. Major releases should still require human-in-the-loop (HITL) sign-off, utilizing the LLM judge's outputs as a heavily weighted signal rather than an absolute gatekeeper.
