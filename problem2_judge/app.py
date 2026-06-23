import sys
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import json

# Add parent to path to import judge pipeline
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from judge.pipeline import LLMJudgePipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM-as-Judge UI")

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LLM Judge Pipeline</title>
            <style>
                :root {
                    --bg-color: #f9f9f9;
                    --text-color: #333;
                    --container-bg: #fff;
                    --border-color: #ddd;
                    --btn-bg: #007bff;
                    --btn-hover: #0056b3;
                    --shadow: rgba(0,0,0,0.1);
                    --card-bg: #fdfdfd;
                }
                [data-theme="dark"] {
                    --bg-color: #121212;
                    --text-color: #e0e0e0;
                    --container-bg: #1e1e1e;
                    --border-color: #333;
                    --btn-bg: #2b7bc4;
                    --btn-hover: #1e5a93;
                    --shadow: rgba(0,0,0,0.5);
                    --card-bg: #2a2a2a;
                }
                body { 
                    font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    max-width: 900px; 
                    margin: 0 auto; 
                    padding: 20px; 
                    background-color: var(--bg-color); 
                    color: var(--text-color);
                    transition: all 0.3s ease;
                }
                .header-container { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
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
                .theme-toggle:hover { background: var(--border-color); }
                .panel {
                    border: 1px solid var(--border-color);
                    background-color: var(--container-bg);
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px var(--shadow);
                    margin-bottom: 20px;
                }
                button.primary {
                    padding: 15px 25px;
                    background-color: var(--btn-bg);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    cursor: pointer;
                    width: 100%;
                    font-weight: bold;
                    transition: background-color 0.2s;
                }
                button.primary:hover { background-color: var(--btn-hover); }
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
                <h1>⚖️ LLM-as-Judge Evaluation Pipeline</h1>
                <button class="theme-toggle" onclick="toggleTheme()">🌓 Toggle Theme</button>
            </div>
            
            <div class="panel">
                <p>Click below to run the pairwise A-vs-B evaluation pipeline. The judge will read the test suite, automatically swap A/B orders to mitigate position bias, and score responses based on the rubric.</p>
                <button class="primary" id="runBtn" onclick="runPipeline()">▶️ Run Pipeline Analysis</button>
            </div>
            
            <div id="resultsArea" style="display: none;">
                <h2>📊 Evaluation Results</h2>
                <div class="panel" id="metricsPanel"></div>
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
                
                async function runPipeline() {
                    const btn = document.getElementById('runBtn');
                    const resultsArea = document.getElementById('resultsArea');
                    const metricsPanel = document.getElementById('metricsPanel');
                    
                    btn.disabled = true;
                    btn.innerText = "⏳ Running Evaluation... (This takes a moment)";
                    resultsArea.style.display = 'none';
                    
                    try {
                        const response = await fetch('/run_eval', { method: 'POST' });
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
                                <p style="font-size: 0.9em; color: #666;"><em>* If flip rate is > 0, it means the judge favored the answer based on its position in the prompt. Our mitigation requires agreement to bypass this!</em></p>
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
                        alert("An error occurred while running the pipeline. Check console and server logs.");
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

@app.post("/run_eval")
async def run_eval_endpoint():
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
        
        pipeline = LLMJudgePipeline()
        suite_path = os.path.join(os.path.dirname(__file__), 'tests', 'suite.json')
        rubric_path = os.path.join(os.path.dirname(__file__), 'judge', 'rubric.yaml')
        
        report = pipeline.run_suite(suite_path, rubric_path)
        return report
    except Exception as e:
        logger.error(f"Error running pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Bind to port 8001 to avoid conflicting with the RAG server on 8000
    uvicorn.run(app, host="0.0.0.0", port=8001)
