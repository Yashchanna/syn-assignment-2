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

## Discussion

### When would you switch back to managed?
I would switch back to a fully managed vector database (like Pinecone or Weaviate Cloud) when:
1. **Scale exceeds single-node limits:** When the vector count reaches the tens/hundreds of millions, requiring distributed sharding, high availability, and replica sets.
2. **Operational Overhead:** When the engineering cost to maintain, back up, and scale a local ChromaDB instance exceeds the SaaS subscription fee.
3. **Advanced Features:** If we need features like serverless scale-to-zero, advanced role-based access control (RBAC), or hybrid search (BM25 + Dense) which managed providers offer out of the box.

### Was retrieval or generation the weak link?
**Generation is the weak link.** 
Retrieval, powered by `sentence-transformers/all-MiniLM-L6-v2` and ChromaDB, is incredibly fast (sub-10ms) and highly accurate for standard semantic queries. However, generation via the LLM API introduces three major bottlenecks:
1. **Latency:** Calling the LLM API takes ~1-3 seconds, dominating the total response time.
2. **Cost:** Token generation scales linearly with usage and forms 99% of the pipeline's operational cost.
3. **Reliability:** The LLM can still occasionally hallucinate or ignore provided context constraints, requiring defensive prompt engineering, whereas retrieval is a deterministic mathematical operation.
