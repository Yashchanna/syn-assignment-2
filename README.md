# Take-Home Assignment: Applied AI / ML Engineering

This repository contains the complete implementation for the "Applied AI / ML Engineering" take-home assignment. It successfully integrates two distinct AI engineering challenges into a **unified FastAPI web application** with a beautifully designed, tabbed dashboard frontend.

### Live Demo (UI Preview Only)
🌐 **[View the Frontend on Vercel](https://syn-assignment-2.vercel.app/)**
*(Note: Due to Vercel's 500MB free-tier serverless limit, the heavy local ML libraries like PyTorch and ChromaDB were excluded from the deployment. The live Vercel link hosts the UI, but querying the API will safely return a mock response explaining the limitation. To experience the actual RAG pipeline and LLM Judge evaluation, please run the application locally!)*

---

## Unified Architecture

To provide an excellent user experience, the two problems were consolidated:
1. **Backend:** A unified FastAPI server (`api/index.py`) exposing two primary endpoints (`/api/query` and `/api/run_eval`).
2. **Frontend:** A vanilla HTML/CSS/JS dashboard (`public/index.html`) featuring a modern Dark Mode, loading animations, and seamless tab switching between the RAG chat interface and the LLM Judge evaluation dashboard.
3. **Data:** Local embedded `chroma_db` for vector storage and JSON/YAML suites for evaluation.

---

## Problem 1: Cost-Efficient RAG Application

**Objective:** Build a QA service backed by a low-cost vector store, including honest evaluation of retrieval, answer quality, cost, and latency.

- **Vector Store:** Embedded **ChromaDB**. It is entirely local and requires no separate cloud infrastructure, making it exceptionally cost-efficient for smaller-scale or privacy-first deployments.
- **Embeddings:** HuggingFace `sentence-transformers` (`all-MiniLM-L6-v2`) generates embeddings entirely locally, saving API costs compared to OpenAI's `text-embedding-3-small`.
- **Generation:** Uses Google's Gemini API (configurable via `.env`) to generate grounded answers with explicit instructions to avoid hallucinations.
- **Latency & Telemetry:** Every query response includes token usage tracking and millisecond latency measurements.

---

## Problem 2: LLM-as-Judge Evaluation Pipeline

**Objective:** Build a pipeline using a strong LLM to automatically score/compare outputs, taking judge biases into account with mitigations and validation.

- **Pipeline Design:** We implemented a Pairwise A-vs-B judging system. 
- **Bias Mitigation:** To mitigate **Position Bias**, the pipeline automatically tests both `A-vs-B` and `B-vs-A` orders. If the judge flips its decision based solely on the order, we detect and flag the flip rate.
- **Evaluation Output:** The UI parses the pipeline results to display the Win Rate for Model A, Win Rate for Model B, Tie Rate, Position Bias Flip Rate, and Token Execution Telemetry.

---

## Local Setup & Full Workflow

Follow these steps to run the full, un-mocked application on your local machine.

### 1. Prerequisites
- Python 3.10+ installed.
- Your AI API Key (Gemini API key is configured by default).

### 2. Environment Configuration
Create a `.env` file in the root of the project:
```ini
OPENAI_API_KEY=your_gemini_or_openai_api_key_here
```

### 3. Install Dependencies
A `requirements-local.txt` file contains the heavy ML dependencies required for the local execution (bypassed in the Vercel deploy).
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements-local.txt
```

### 4. Run the Unified Server
```powershell
python api/index.py
```
*(Or use `uvicorn api.index:app --host 0.0.0.0 --port 8000`)*

### 5. Access the Dashboard
Open your browser and navigate to:
**[http://localhost:8000](http://localhost:8000)**

- **Tab 1 (RAG Assistant):** Type a query into the chatbox. The backend will embed your query locally, retrieve the top-K chunks from the embedded ChromaDB, and stream the grounded answer along with source citations and execution latency.
- **Tab 2 (LLM Judge):** Click "Run Pipeline Analysis". The backend will load the adversarial JSON test suite, parse the YAML rubric, run the A-vs-B evaluations (including bias mitigation swapping), and return the full statistical analysis directly to the UI.

---

## Project Structure

```text
/
├── api/
│   ├── index.py                  # Unified FastAPI Entrypoint
│   ├── config.py                 # Environment configurations
│   ├── rag_logic.py              # Extracted logic for RAG retrieval
│   └── judge_logic.py            # Extracted logic for Pairwise LLM Judge
├── public/
│   └── index.html                # Unified HTML/CSS/JS Frontend Dashboard
├── data/
│   ├── suite.json                # Test suite for the LLM Judge
│   └── rubric.yaml               # Evaluation rubric for the LLM Judge
├── problem1_rag/                 # Original RAG ingestion and evaluation harness
├── problem2_judge/               # Original Judge validation scripts
├── chroma_db/                    # Local SQLite vector database
├── requirements.txt              # Lightweight requirements for Vercel
├── requirements-local.txt        # Full ML requirements for local execution
├── vercel.json                   # Vercel deployment routing configuration
└── README.md                     # This file
```
