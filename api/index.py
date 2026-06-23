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
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
                
                :root {
                    --bg-gradient: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
                    --text-color: #1e293b;
                    --container-bg: rgba(255, 255, 255, 0.85);
                    --border-color: rgba(255, 255, 255, 0.5);
                    --user-msg-bg: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                    --user-msg-color: white;
                    --bot-msg-bg: rgba(255, 255, 255, 0.9);
                    --bot-msg-color: #334155;
                    --input-bg: rgba(255, 255, 255, 0.9);
                    --btn-bg: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
                    --btn-hover: linear-gradient(135deg, #4338ca 0%, #2563eb 100%);
                    --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
                    --card-bg: rgba(255, 255, 255, 0.6);
                    --tab-active-bg: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
                    --tab-inactive-bg: rgba(226, 232, 240, 0.8);
                    --tab-active-color: white;
                    --tab-inactive-color: #475569;
                    --glass-backdrop: blur(12px);
                }
                [data-theme="dark"] {
                    --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                    --text-color: #f8fafc;
                    --container-bg: rgba(30, 41, 59, 0.7);
                    --border-color: rgba(255, 255, 255, 0.08);
                    --user-msg-bg: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                    --user-msg-color: white;
                    --bot-msg-bg: rgba(51, 65, 85, 0.8);
                    --bot-msg-color: #e2e8f0;
                    --input-bg: rgba(30, 41, 59, 0.8);
                    --btn-bg: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
                    --btn-hover: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
                    --shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.5);
                    --card-bg: rgba(30, 41, 59, 0.5);
                    --tab-active-bg: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
                    --tab-inactive-bg: rgba(51, 65, 85, 0.5);
                    --tab-active-color: white;
                    --tab-inactive-color: #94a3b8;
                }
                body { 
                    font-family: 'Inter', sans-serif; 
                    max-width: 1000px; 
                    margin: 0 auto; 
                    padding: 30px 20px; 
                    background: var(--bg-gradient); 
                    color: var(--text-color);
                    transition: all 0.4s ease;
                    min-height: 100vh;
                }
                .header-container { 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center; 
                    margin-bottom: 30px; 
                    padding-bottom: 20px;
                    border-bottom: 1px solid var(--border-color);
                }
                h1 { 
                    margin: 0; 
                    font-size: 28px; 
                    font-weight: 700;
                    background: var(--btn-bg);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                .theme-toggle {
                    background: var(--container-bg);
                    border: 1px solid var(--border-color);
                    color: var(--text-color);
                    padding: 10px 16px;
                    border-radius: 12px;
                    cursor: pointer;
                    font-weight: 600;
                    backdrop-filter: var(--glass-backdrop);
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }
                .theme-toggle:hover { 
                    transform: translateY(-2px);
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                }
                
                /* Tabs */
                .tabs { 
                    display: flex; 
                    gap: 12px; 
                    margin-bottom: 25px; 
                }
                .tab-btn {
                    padding: 12px 24px;
                    border: 1px solid var(--border-color);
                    border-radius: 12px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: 600;
                    background: var(--tab-inactive-bg);
                    color: var(--tab-inactive-color);
                    backdrop-filter: var(--glass-backdrop);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }
                .tab-btn:hover:not(.active) {
                    transform: translateY(-2px);
                    background: var(--card-bg);
                }
                .tab-btn.active {
                    background: var(--tab-active-bg);
                    color: var(--tab-active-color);
                    box-shadow: var(--shadow);
                    border-color: transparent;
                }
                .tab-content { display: none; animation: slideUp 0.4s ease forwards; opacity: 0; transform: translateY(10px); }
                .tab-content.active { display: block; }
                
                @keyframes slideUp { 
                    to { opacity: 1; transform: translateY(0); } 
                }

                /* Panel Elements */
                .panel {
                    border: 1px solid var(--border-color);
                    background: var(--container-bg);
                    backdrop-filter: var(--glass-backdrop);
                    padding: 25px;
                    border-radius: 16px;
                    box-shadow: var(--shadow);
                    margin-bottom: 25px;
                }
                
                /* Chatbox specific styles */
                #chatbox { 
                    height: 500px; 
                    border: 1px solid var(--border-color); 
                    background: var(--container-bg); 
                    backdrop-filter: var(--glass-backdrop);
                    overflow-y: auto; 
                    padding: 25px; 
                    margin-bottom: 20px; 
                    border-radius: 16px; 
                    box-shadow: var(--shadow); 
                    scroll-behavior: smooth;
                }
                #chatbox::-webkit-scrollbar { width: 8px; }
                #chatbox::-webkit-scrollbar-thumb { background: rgba(156, 163, 175, 0.5); border-radius: 4px; }

                .message { 
                    margin-bottom: 18px; 
                    padding: 16px 20px; 
                    border-radius: 16px; 
                    max-width: 80%; 
                    line-height: 1.6; 
                    font-size: 15px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                    animation: messageFade 0.3s ease;
                }
                @keyframes messageFade { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }

                .user-message { 
                    background: var(--user-msg-bg); 
                    color: var(--user-msg-color); 
                    margin-left: auto; 
                    border-bottom-right-radius: 4px;
                }
                .bot-message { 
                    background: var(--bot-msg-bg); 
                    color: var(--bot-msg-color); 
                    border-bottom-left-radius: 4px;
                    border: 1px solid var(--border-color);
                }
                .citations { 
                    font-size: 0.8em; 
                    color: var(--tab-inactive-color); 
                    margin-top: 10px; 
                    border-top: 1px solid var(--border-color); 
                    padding-top: 8px; 
                    opacity: 0.8;
                }
                .input-area { display: flex; gap: 12px; }
                input[type="text"] { 
                    flex: 1; 
                    padding: 16px 20px; 
                    border: 1px solid var(--border-color); 
                    border-radius: 12px; 
                    font-size: 16px; 
                    outline: none; 
                    background: var(--input-bg); 
                    color: var(--text-color);
                    backdrop-filter: var(--glass-backdrop);
                    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
                    transition: border-color 0.3s;
                }
                input[type="text"]:focus { 
                    border-color: #6366f1; 
                    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
                }
                
                /* Buttons */
                button.primary {
                    padding: 16px 30px;
                    background: var(--btn-bg);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 16px;
                    cursor: pointer;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                    box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.39);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }
                button.primary:hover { 
                    background: var(--btn-hover); 
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
                }
                button.primary:disabled {
                    opacity: 0.7;
                    cursor: not-allowed;
                    transform: none;
                }
                button.primary.full-width { width: 100%; margin-top: 10px; }

                /* Cards */
                .result-card {
                    background: var(--card-bg);
                    border: 1px solid var(--border-color);
                    border-radius: 12px;
                    padding: 20px;
                    margin-top: 15px;
                    backdrop-filter: var(--glass-backdrop);
                    transition: transform 0.3s;
                }
                .result-card:hover { transform: translateY(-3px); box-shadow: var(--shadow); }
                .result-card h3 { margin-top: 0; color: #4f46e5; }
                [data-theme="dark"] .result-card h3 { color: #818cf8; }
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
        gen_res = generate_answer(req.query, chunks)
        answer = gen_res["answer"]
        tokens = {"prompt_tokens": gen_res["prompt_tokens"], "completion_tokens": gen_res["completion_tokens"]}
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
