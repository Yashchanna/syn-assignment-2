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
