# Cost Analysis: ChromaDB vs Managed Vector DBs

This document compares the monthly cost of running our Cost-Efficient RAG application (using embedded ChromaDB) against fully managed vector databases (like Pinecone) at scale.

## Assumptions
- **Vector Dimensions:** 384 (all-MiniLM-L6-v2)
- **Metadata per vector:** ~500 bytes
- **Managed DB Pricing (Pinecone Standard):** ~$70/month for ~1M vectors (1 pod). Scale linearly for simplicity.
- **Self-Hosted (ChromaDB on EC2):** 
  - t3.micro (2 vCPU, 1 GB RAM): ~$7.50/month (Good for ~100K vectors)
  - t3.small (2 vCPU, 2 GB RAM): ~$15/month (Good for ~1M vectors)
  - t3.large (2 vCPU, 8 GB RAM): ~$60/month (Good for ~10M vectors)
  - EBS volume: ~$0.08 per GB/month

## Cost Comparison Table

| Scale (Vectors) | ChromaDB (Self-Hosted EC2) | Managed DB (e.g., Pinecone) | Cost Savings |
|-----------------|----------------------------|-----------------------------|--------------|
| 100K            | ~$8 / month (t3.micro)     | ~$70 / month                | ~88%         |
| 1 Million       | ~$16 / month (t3.small)    | ~$70 / month                | ~77%         |
| 10 Million      | ~$65 / month (t3.large)    | ~$700 / month               | ~90%         |

## Trade-offs
- **When to switch back to managed:** If query latency spikes unacceptably under concurrent high-throughput load, or if managing EC2 infrastructure (updates, backups) becomes more expensive in developer time than the SaaS subscription.
- **Weak Link:** In most low-cost setups, the embedding generation or LLM text generation is the bottleneck (both in latency and cost) rather than vector retrieval.
