# Problem 1: Cost-Efficient RAG Application

This directory contains the solution to Problem 1. We use **ChromaDB** as an embedded vector database to significantly reduce costs compared to fully managed options like Pinecone, while maintaining fast retrieval latency.

## How to Run

1. Ensure your `.env` file is set up with your `OPENAI_API_KEY` at the root directory.
2. Add some documents (`.pdf`, `.md`, `.html`) to the `problem1_rag/corpus/` directory (you may need to create this folder).
3. Ingest the documents:
   ```bash
   python app/ingest.py
   ```
4. Start the FastAPI server:
   ```bash
   python app/main.py
   ```
5. You can now query the endpoint:
   ```bash
   curl -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" -d '{"query": "What is in the document?", "k": 5}'
   ```

## Evaluation

To run the evaluation harness (computes hit rate and average latency over a fixed dataset):
Ensure the API server is running, then in another terminal:
```bash
python eval/eval_harness.py
```

## Cost Analysis
Please refer to `cost_analysis.md` for a breakdown of costs versus a managed vector DB.
