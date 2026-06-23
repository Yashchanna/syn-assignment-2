# 🎥 Video Walkthrough Script: Applied AI Engineering Assignment

*Tip: Have this script open on a second monitor or printed out so you can reference it while you record. Keep your screen recording focused on your browser and IDE.*

## 🎬 Section 1: Introduction (0:00 - 0:30)
**Visual:** Have your GitHub repository open on the screen, showing the `README.md`.
**Voiceover:**
> "Hi everyone, I'm Yash Channa, and today I'll be walking you through my submission for the Applied AI and Machine Learning Engineering assignment. Instead of building two isolated scripts, I took the initiative to integrate both problems—the Cost-Efficient RAG Application and the LLM-as-Judge Evaluation Pipeline—into a single, unified full-stack application."

## 🚀 Section 2: Architecture & Setup Overview (0:30 - 1:15)
**Visual:** Switch to your IDE (VS Code/PyCharm) and briefly show the directory structure (`api/`, `public/`, `data/`). Then show your terminal where the local server is running.
**Voiceover:**
> "Let's look at the architecture. I used FastAPI to build a unified backend that handles both the RAG pipeline and the LLM-Judge pipeline. The frontend is a vanilla HTML and CSS dashboard designed with a modern dark mode. Because the machine learning libraries like PyTorch and ChromaDB exceed Vercel's free serverless limits, I deployed the frontend UI to Vercel in a 'mock mode' for easy viewing, while the actual heavy machine learning execution happens via this local server I have running here on port 8000."

## 📚 Section 3: Problem 1 - Cost-Efficient RAG Application (1:15 - 2:30)
**Visual:** Open your browser and go to `http://localhost:8000`. Show the "Problem 1: RAG Assistant" tab. Type a question related to the uploaded PDF corpus and hit 'Send Query'. 
**Voiceover:**
> "Here is the unified dashboard. Let's start with Problem 1: The Cost-Efficient RAG Application. 
> 
> My primary goal here was cost efficiency. Instead of using a paid cloud vector database and paid embedding APIs, I embedded a local instance of ChromaDB and used HuggingFace's open-source `sentence-transformers` to generate embeddings locally. The only API cost is the final generation step using the LLM.
>
> *(Wait for the response to load)*
> As you can see, when I ask a question, the system retrieves the relevant chunks, feeds them into the grounded LLM prompt, and streams back an answer. Importantly, it includes the exact source citations and logs the execution latency and token usage, which is crucial for production telemetry."

## ⚖️ Section 4: Problem 2 - LLM-as-Judge Pipeline (2:30 - 4:00)
**Visual:** Click the "Problem 2: LLM Judge" tab. Click the "Run Pipeline Analysis" button. While it's loading, switch to your IDE and quickly show `data/suite.json` and `data/rubric.yaml`.
**Voiceover:**
> "Moving on to Problem 2, I built an LLM-as-a-Judge pipeline. 
> 
> I designed this as a Pairwise A-versus-B evaluator. The system reads from a structured JSON test suite and evaluates responses based on a YAML rubric.
> 
> One of the biggest challenges with LLM judges is **Position Bias**—where the judge tends to favor whichever model is presented first. To mitigate this, my pipeline automatically tests both permutations: Model A vs B, and then Model B vs A. 
>
> *(Switch back to the browser to show the results that just loaded)*
> Here are the results. The UI parses the backend evaluation and shows the win rates. It also explicitly tracks the 'Position Bias Flip Rate'—which tells us how often the judge changed its mind just because the order of the answers was swapped. This ensures our evaluation metrics are highly reliable and untainted by prompting artifacts."

## 🏁 Section 5: Conclusion (4:00 - 4:30)
**Visual:** Switch back to the GitHub repository or the Vercel live link.
**Voiceover:**
> "In summary, this unified architecture effectively demonstrates how to build a scalable, cost-efficient RAG system and a highly rigorous LLM evaluation pipeline that actively detects and mitigates bias. The code is modular, fully documented, and ready for review. 
> 
> Thank you for your time, and I look forward to discussing the technical details further!"
