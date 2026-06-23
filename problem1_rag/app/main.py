import time
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.retrieve import retrieve_chunks, generate_answer

from fastapi.responses import HTMLResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cost-Efficient RAG Service")

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>RAG QA Service</title>
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
                }
                body { 
                    font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    max-width: 800px; 
                    margin: 0 auto; 
                    padding: 20px; 
                    background-color: var(--bg-color); 
                    color: var(--text-color);
                    transition: all 0.3s ease;
                }
                .header-container {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }
                h1 { margin: 0; }
                .theme-toggle {
                    background: var(--container-bg);
                    border: 1px solid var(--border-color);
                    color: var(--text-color);
                    padding: 8px 12px;
                    border-radius: 6px;
                    cursor: pointer;
                    transition: all 0.2s;
                }
                .theme-toggle:hover {
                    background: var(--bot-msg-bg);
                }
                #chatbox { 
                    height: 500px; 
                    border: 1px solid var(--border-color); 
                    background-color: var(--container-bg); 
                    overflow-y: auto; 
                    padding: 20px; 
                    margin-bottom: 15px; 
                    border-radius: 8px; 
                    box-shadow: 0 4px 6px var(--shadow); 
                    transition: all 0.3s ease;
                }
                .message { 
                    margin-bottom: 15px; 
                    padding: 15px; 
                    border-radius: 8px; 
                    max-width: 80%; 
                    line-height: 1.5; 
                }
                .user-message { 
                    background-color: var(--user-msg-bg); 
                    color: var(--user-msg-color); 
                    margin-left: auto; 
                }
                .bot-message { 
                    background-color: var(--bot-msg-bg); 
                    color: var(--bot-msg-color); 
                }
                .citations { 
                    font-size: 0.85em; 
                    color: #888; 
                    margin-top: 8px; 
                    border-top: 1px solid var(--border-color); 
                    padding-top: 5px; 
                }
                .input-area { display: flex; gap: 10px; }
                input[type="text"] { 
                    flex: 1; 
                    padding: 15px; 
                    border: 1px solid var(--border-color); 
                    border-radius: 8px; 
                    font-size: 16px; 
                    outline: none; 
                    background-color: var(--input-bg);
                    color: var(--text-color);
                }
                input[type="text"]:focus { border-color: var(--btn-bg); }
                .send-btn { 
                    padding: 15px 25px; 
                    background-color: var(--btn-bg); 
                    color: white; 
                    border: none; 
                    border-radius: 8px; 
                    font-size: 16px; 
                    cursor: pointer; 
                    transition: background-color 0.2s; 
                }
                .send-btn:hover { background-color: var(--btn-hover); }
            </style>
        </head>
        <body>
            <div class="header-container">
                <h1>📚 Document QA Assistant</h1>
                <button class="theme-toggle" onclick="toggleTheme()">🌓 Toggle Dark Mode</button>
            </div>
            <div id="chatbox">
                <div class="message bot-message">Hello! I am ready to answer questions based on the documents in your corpus. What would you like to know?</div>
            </div>
            <div class="input-area">
                <input type="text" id="queryInput" placeholder="Ask a question..." onkeypress="if(event.key === 'Enter') sendQuery()">
                <button class="send-btn" onclick="sendQuery()">Send</button>
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
                async function sendQuery() {
                    const input = document.getElementById('queryInput');
                    const chatbox = document.getElementById('chatbox');
                    const query = input.value.trim();
                    if (!query) return;
                    
                    // Add user message
                    chatbox.innerHTML += `<div class="message user-message">${query}</div>`;
                    input.value = '';
                    chatbox.scrollTop = chatbox.scrollHeight;
                    
                    // Add loading indicator
                    const loadingId = 'loading-' + Date.now();
                    chatbox.innerHTML += `<div id="${loadingId}" class="message bot-message" style="color: #888;">Thinking...</div>`;
                    chatbox.scrollTop = chatbox.scrollHeight;
                    
                    try {
                        const response = await fetch('/query', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ query: query, k: 5 })
                        });
                        const data = await response.json();
                        
                        document.getElementById(loadingId).remove();
                        
                        let citationsHtml = '';
                        if (data.citations && data.citations.length > 0) {
                            const sources = [...new Set(data.citations.map(c => c.source))].join(', ');
                            citationsHtml = `<div class="citations"><strong>Sources:</strong> ${sources}</div>`;
                        }
                        
                        // Simple Markdown to HTML for the answer
                        let formattedAnswer = data.answer.replace(/\\n/g, '<br>');
                        
                        chatbox.innerHTML += `<div class="message bot-message">${formattedAnswer}${citationsHtml}</div>`;
                    } catch (e) {
                        document.getElementById(loadingId).remove();
                        chatbox.innerHTML += `<div class="message bot-message" style="color: red;">Error: Could not process request. Make sure the backend is running properly.</div>`;
                    }
                    chatbox.scrollTop = chatbox.scrollHeight;
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

class QueryRequest(BaseModel):
    query: str
    k: int = 5

class QueryResponse(BaseModel):
    answer: str
    chunks_retrieved: int
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    citations: list[dict]

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(req: QueryRequest):
    start_time = time.time()
    
    try:
        # Retrieve
        chunks = retrieve_chunks(req.query, k=req.k)
        
        # Generate
        gen_result = generate_answer(req.query, chunks)
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Log telemetry
        logger.info(
            f"Query processed. Latency: {latency_ms:.2f}ms, "
            f"Chunks retrieved: {len(chunks)}, "
            f"Tokens: {gen_result['total_tokens']}"
        )
        
        return QueryResponse(
            answer=gen_result['answer'],
            chunks_retrieved=len(chunks),
            latency_ms=latency_ms,
            prompt_tokens=gen_result['prompt_tokens'],
            completion_tokens=gen_result['completion_tokens'],
            total_tokens=gen_result['total_tokens'],
            citations=[{"id": c['id'], "source": c['metadata'].get('source')} for c in chunks]
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
