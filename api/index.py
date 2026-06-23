import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Ensure root is in Python path for Vercel execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from problem1_rag.app.retrieve import retrieve_chunks, generate_answer
    from problem2_judge.judge.pipeline import LLMJudgePipeline
    ML_LIBS_AVAILABLE = True
except ImportError:
    ML_LIBS_AVAILABLE = False
    print("Warning: Heavy ML libraries (Chroma/SentenceTransformers) not found. Running in UI-only/Mock mode for Vercel.")

app = FastAPI(title="Unified AI Assignment - Vercel")

@app.get("/", response_class=HTMLResponse)
async def get_unified_ui():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Applied AI Assignment - Unified Dashboard</title>
            <style>
                :root {
                    --bg-color: #f9f9f9;
                    --text-color: #333;
                    --container-bg: #fff;
                    --border-color: #ddd;
                    --user-msg-bg: #007bff;
                    --user-msg-color: white;
                    --bot-msg-bg: #f1f1f1;
                    --bot-msg-color: #333;
                    --input-bg: #fff;
                    --btn-bg: #007bff;
                    --btn-hover: #0056b3;
                    --shadow: rgba(0,0,0,0.1);
                    --card-bg: #fdfdfd;
                    --tab-active-bg: #007bff;
                    --tab-inactive-bg: #e9ecef;
                    --tab-active-color: white;
                    --tab-inactive-color: #495057;
                }
                [data-theme="dark"] {
                    --bg-color: #121212;
                    --text-color: #e0e0e0;
                    --container-bg: #1e1e1e;
                    --border-color: #333;
                    --user-msg-bg: #2b7bc4;
                    --user-msg-color: white;
                    --bot-msg-bg: #2a2a2a;
                    --bot-msg-color: #e0e0e0;
                    --input-bg: #2a2a2a;
                    --btn-bg: #2b7bc4;
                    --btn-hover: #1e5a93;
                    --shadow: rgba(0,0,0,0.5);
                    --card-bg: #2a2a2a;
                    --tab-active-bg: #2b7bc4;
                    --tab-inactive-bg: #2a2a2a;
                    --tab-active-color: white;
                    --tab-inactive-color: #aaa;
                }
                body { 
                    font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    max-width: 1000px; 
                    margin: 0 auto; 
                    padding: 20px; 
                    background-color: var(--bg-color); 
                    color: var(--text-color);
                    transition: all 0.3s ease;
                }
                .header-container { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
                h1 { margin: 0; font-size: 24px; }
                .theme-toggle {
                    background: var(--container-bg);
                    border: 1px solid var(--border-color);
                    color: var(--text-color);
                    padding: 8px 12px;
                    border-radius: 6px;
                    cursor: pointer;
                    transition: all 0.2s;
                }
                .theme-toggle:hover { background: var(--border-color); }
                
                /* Tabs */
                .tabs { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid var(--border-color); padding-bottom: 10px; }
                .tab-btn {
                    padding: 10px 20px;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: bold;
                    background-color: var(--tab-inactive-bg);
                    color: var(--tab-inactive-color);
                    transition: all 0.2s;
                }
                .tab-btn.active {
                    background-color: var(--tab-active-bg);
                    color: var(--tab-active-color);
                    box-shadow: 0 2px 4px var(--shadow);
                }
                .tab-content { display: none; animation: fadeIn 0.3s; }
                .tab-content.active { display: block; }
                
                @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

                /* Panel Elements */
                .panel {
                    border: 1px solid var(--border-color);
                    background-color: var(--container-bg);
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px var(--shadow);
                    margin-bottom: 20px;
                }
                
                /* Chatbox specific styles */
                #chatbox { 
                    height: 500px; 
                    border: 1px solid var(--border-color); 
                    background-color: var(--container-bg); 
                    overflow-y: auto; 
                    padding: 20px; 
                    margin-bottom: 15px; 
                    border-radius: 8px; 
                    box-shadow: 0 4px 6px var(--shadow); 
                }
                .message { margin-bottom: 15px; padding: 15px; border-radius: 8px; max-width: 80%; line-height: 1.5; }
                .user-message { background-color: var(--user-msg-bg); color: var(--user-msg-color); margin-left: auto; }
                .bot-message { background-color: var(--bot-msg-bg); color: var(--bot-msg-color); }
                .citations { font-size: 0.85em; color: #888; margin-top: 8px; border-top: 1px solid var(--border-color); padding-top: 5px; }
                .input-area { display: flex; gap: 10px; }
                input[type="text"] { 
                    flex: 1; padding: 15px; border: 1px solid var(--border-color); 
                    border-radius: 8px; font-size: 16px; outline: none; 
                    background-color: var(--input-bg); color: var(--text-color);
                }
                input[type="text"]:focus { border-color: var(--btn-bg); }
                
                /* Buttons */
                button.primary {
                    padding: 15px 25px;
                    background-color: var(--btn-bg);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    cursor: pointer;
                    font-weight: bold;
                    transition: background-color 0.2s;
                }
                button.primary:hover { background-color: var(--btn-hover); }
                button.primary.full-width { width: 100%; }

                /* Cards */
                .result-card {
                    background-color: var(--card-bg);
                    border: 1px solid var(--border-color);
                    border-radius: 6px;
                    padding: 15px;
                    margin-top: 15px;
                }
            </style>
        </head>
        <body>
            <div class="header-container">
                <h1>🚀 Unified AI Assignment Dashboard</h1>
                <button class="theme-toggle" onclick="toggleTheme()">🌓 Toggle Dark Mode</button>
            </div>
            
            <div class="tabs">
                <button class="tab-btn active" onclick="switchTab('rag')">Problem 1: RAG Assistant</button>
                <button class="tab-btn" onclick="switchTab('judge')">Problem 2: LLM Judge</button>
            </div>

            <!-- Problem 1: RAG -->
            <div id="rag-tab" class="tab-content active">
                <div id="chatbox">
                    <div class="message bot-message">Hello! I am ready to answer questions based on the documents in your vector corpus. What would you like to know?</div>
                </div>
                <div class="input-area">
                    <input type="text" id="queryInput" placeholder="Ask a question..." onkeypress="if(event.key === 'Enter') sendQuery()">
                    <button class="primary" onclick="sendQuery()">Send Query</button>
                </div>
            </div>

            <!-- Problem 2: LLM Judge -->
            <div id="judge-tab" class="tab-content">
                <div class="panel">
                    <h2>⚖️ LLM-as-Judge Evaluation Pipeline</h2>
                    <p>Click below to run the pairwise A-vs-B evaluation pipeline. The judge will read the test suite, automatically swap A/B orders to mitigate position bias, and score responses based on the rubric.</p>
                    <button class="primary full-width" id="runBtn" onclick="runPipeline()">▶️ Run Pipeline Analysis</button>
                </div>
                
                <div id="resultsArea" style="display: none;">
                    <h2>📊 Evaluation Results</h2>
                    <div class="panel" id="metricsPanel"></div>
                </div>
            </div>

            <script>
                function toggleTheme() {
                    const html = document.documentElement;
                    if (html.getAttribute('data-theme') === 'dark') {
                        html.removeAttribute('data-theme');
                    } else {
                        html.setAttribute('data-theme', 'dark');
                    }
                }

                function switchTab(tabId) {
                    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
                    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
                    
                    document.getElementById(tabId + '-tab').classList.add('active');
                    event.target.classList.add('active');
                }
                
                // Problem 1 Logic
                async function sendQuery() {
                    const input = document.getElementById('queryInput');
                    const chatbox = document.getElementById('chatbox');
                    const query = input.value.trim();
                    if (!query) return;
                    
                    chatbox.innerHTML += `<div class="message user-message">${query}</div>`;
                    input.value = '';
                    chatbox.scrollTop = chatbox.scrollHeight;
                    
                    const loadingId = 'loading-' + Date.now();
                    chatbox.innerHTML += `<div id="${loadingId}" class="message bot-message" style="color: #888;">Searching and generating...</div>`;
                    chatbox.scrollTop = chatbox.scrollHeight;
                    
                    try {
                        const response = await fetch('/api/query', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ query: query, k: 5 })
                        });
                        
                        if (!response.ok) throw new Error("API Error");
                        
                        const data = await response.json();
                        document.getElementById(loadingId).remove();
                        
                        let citationsHtml = '';
                        if (data.citations && data.citations.length > 0) {
                            const sources = [...new Set(data.citations.map(c => c.source))].join(', ');
                            citationsHtml = `<div class="citations"><strong>Sources:</strong> ${sources} | <strong>Latency:</strong> ${data.latency_ms.toFixed(0)}ms</div>`;
                        }
                        
                        let formattedAnswer = data.answer.replace(/\\n/g, '<br>');
                        chatbox.innerHTML += `<div class="message bot-message">${formattedAnswer}${citationsHtml}</div>`;
                    } catch (e) {
                        document.getElementById(loadingId).remove();
                        chatbox.innerHTML += `<div class="message bot-message" style="color: red;">Error: Could not process request. Server might be down or quota exceeded.</div>`;
                    }
                    chatbox.scrollTop = chatbox.scrollHeight;
                }

                // Problem 2 Logic
                async function runPipeline() {
                    const btn = document.getElementById('runBtn');
                    const resultsArea = document.getElementById('resultsArea');
                    const metricsPanel = document.getElementById('metricsPanel');
                    
                    btn.disabled = true;
                    btn.innerText = "⏳ Running Evaluation... (This takes a moment)";
                    resultsArea.style.display = 'none';
                    
                    try {
                        const response = await fetch('/api/run_eval', { method: 'POST' });
                        
                        if (!response.ok) throw new Error("API Error");
                        const data = await response.json();
                        
                        let html = `
                            <div class="result-card">
                                <h3>🏆 Win Rates</h3>
                                <p><strong>Model A:</strong> ${(data.model_a_win_rate * 100).toFixed(1)}%</p>
                                <p><strong>Model B:</strong> ${(data.model_b_win_rate * 100).toFixed(1)}%</p>
                                <p><strong>Ties:</strong> ${(data.tie_rate * 100).toFixed(1)}%</p>
                            </div>
                            <div class="result-card">
                                <h3>⚖️ Bias Analysis</h3>
                                <p><strong>Position Bias (Flip Rate):</strong> ${(data.position_bias_flip_rate * 100).toFixed(1)}%</p>
                                <p style="font-size: 0.9em; color: #666;"><em>* If flip rate is > 0, the judge favored the answer based on its position in the prompt.</em></p>
                            </div>
                            <div class="result-card">
                                <h3>⚙️ Execution Telemetry</h3>
                                <p><strong>Total Cases Evaluated:</strong> ${data.total_cases}</p>
                                <p><strong>Tokens Used:</strong> Prompt: ${data.tokens.prompt_tokens} | Completion: ${data.tokens.completion_tokens}</p>
                            </div>
                        `;
                        metricsPanel.innerHTML = html;
                        resultsArea.style.display = 'block';
                    } catch (e) {
                        alert("An error occurred while running the pipeline. Server might be down or quota exceeded.");
                    } finally {
                        btn.disabled = false;
                        btn.innerText = "▶️ Run Pipeline Analysis";
                    }
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# --- Problem 1: RAG API ---
class RAGQueryRequest(BaseModel):
    query: str
    k: int = 5

class RAGQueryResponse(BaseModel):
    answer: str
    citations: list
    latency_ms: float
    tokens: dict

@app.post("/api/query", response_model=RAGQueryResponse)
async def api_query(req: RAGQueryRequest):
    import time
    start = time.time()
    if not ML_LIBS_AVAILABLE:
        return RAGQueryResponse(
            answer="**Vercel Deployment Limitation:** The heavy ML libraries (PyTorch/ChromaDB/SentenceTransformers) exceed Vercel's 500MB Serverless limit and were removed to allow the UI to deploy. Please run the backend locally to test full RAG functionality!",
            citations=[],
            latency_ms=10.0,
            tokens={"prompt_tokens": 0, "completion_tokens": 0}
        )
    try:
        chunks = retrieve_chunks(req.query, k=req.k)
        answer, tokens = generate_answer(req.query, chunks)
        latency = (time.time() - start) * 1000
        citations = [{"source": c.metadata.get("source", "Unknown")} for c in chunks]
        return RAGQueryResponse(
            answer=answer,
            citations=citations,
            latency_ms=latency,
            tokens=tokens
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Problem 2: LLM Judge API ---
@app.post("/api/run_eval")
async def api_run_eval():
    if not ML_LIBS_AVAILABLE:
        return {
            "model_a_win_rate": 0.5,
            "model_b_win_rate": 0.5,
            "tie_rate": 0.0,
            "position_bias_flip_rate": 0.0,
            "total_cases": "N/A (Vercel Limitation)",
            "tokens": {"prompt_tokens": 0, "completion_tokens": 0}
        }
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        pipeline = LLMJudgePipeline()
        suite_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'suite.json')
        rubric_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'rubric.yaml')
        
        report = pipeline.run_suite(suite_path, rubric_path)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
