# Sample Input & Output

This document provides concrete examples of the data structures flowing into and out of the unified API backend for both Problem 1 (RAG) and Problem 2 (LLM-as-Judge).

---

## 📚 Problem 1: Cost-Efficient RAG Application

### Sample Input (API Request)
*Endpoint: `POST /api/query`*
```json
{
  "query": "What are the primary metrics used to evaluate the LLM-as-a-Judge pipeline?",
  "k": 3
}
```

### Sample Output (API Response)
```json
{
  "answer": "Based on the provided document, the primary metrics used to evaluate the LLM-as-a-Judge pipeline are the Win Rate for Model A and Model B, the Tie Rate, and the Position Bias Flip Rate, which measures how often the judge changes its verdict based solely on the order of presentation [Document 1].",
  "citations": [
    {
      "source": "Gen AI_assignment.pdf"
    }
  ],
  "latency_ms": 1452.3,
  "tokens": {
    "prompt_tokens": 1024,
    "completion_tokens": 58
  }
}
```

---

## ⚖️ Problem 2: LLM-as-Judge Evaluation Pipeline

### Sample Input (Test Suite Entry)
*File: `data/suite.json`*
```json
{
  "id": "tc1",
  "prompt": "Explain the difference between a list and a tuple in Python.",
  "model_a_output": "A list is mutable and defined with square brackets []. A tuple is immutable and defined with parentheses (). Lists are generally used for homogeneous data that might change, while tuples are used for heterogeneous data that should remain constant.",
  "model_b_output": "Lists are [], tuples are ()."
}
```

### Sample Input (Rubric)
*File: `data/rubric.yaml`*
```yaml
name: "General Programming QA Rubric"
criteria:
  - id: "completeness"
    description: "Does the answer fully address the prompt?"
  - id: "correctness"
    description: "Is the technical information accurate?"
  - id: "conciseness"
    description: "Is the answer free of unnecessary filler or padding?"
```

### Sample Output (API Pipeline Report)
*Endpoint: `POST /api/run_eval`*
```json
{
  "model_a_win_rate": 0.8,
  "model_b_win_rate": 0.0,
  "tie_rate": 0.2,
  "position_bias_flip_rate": 0.0,
  "total_cases": 1,
  "tokens": {
    "prompt_tokens": 850,
    "completion_tokens": 120
  }
}
```

*(Note: The `position_bias_flip_rate` is 0.0 because the pipeline automatically intercepted any flipped verdicts and forced them into the `tie_rate` bucket, actively neutralizing the bias.)*
