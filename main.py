import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from tinyfish import AsyncTinyFish
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="WebScout AI",
    description="Goal-driven live web scouting powered by TinyFish Agent SDK",
    version="1.0.0"
)

api_key = os.getenv("TINYFISH_API_KEY")
if not api_key:
    raise ValueError("TINYFISH_API_KEY is missing in .env file")

client = AsyncTinyFish(api_key=api_key)

class ScoutRequest(BaseModel):
    url: str
    goal: str

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>WebScout AI - Live Web Agent</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-900 text-white min-h-screen p-8">
        <div class="max-w-3xl mx-auto">
            <h1 class="text-4xl font-bold text-cyan-400 mb-2">WebScout AI</h1>
            <p class="text-slate-400 mb-6">Autonomous Goal-Driven Web Scouting powered by <b>TinyFish Agent SDK</b></p>
            
            <div class="bg-slate-800 p-6 rounded-xl shadow-lg border border-slate-700 space-y-4">
                <div>
                    <label class="block text-sm text-slate-300 mb-1">Target Website URL</label>
                    <input id="url" type="text" value="https://news.ycombinator.com" class="w-full p-3 rounded bg-slate-900 border border-slate-600 text-white">
                </div>
                <div>
                    <label class="block text-sm text-slate-300 mb-1">Scouting Goal (Plain English)</label>
                    <input id="goal" type="text" value="Extract top 5 headline titles" class="w-full p-3 rounded bg-slate-900 border border-slate-600 text-white">
                </div>
                <button onclick="runScout()" id="btn" class="w-full bg-cyan-500 hover:bg-cyan-600 text-slate-900 font-bold py-3 rounded transition">
                    Launch TinyFish Web Agent
                </button>
            </div>

            <div id="loading" class="hidden mt-6 text-center text-cyan-400 animate-pulse">
                TinyFish remote browser agent is navigating the live page... Please wait (10-20s)...
            </div>

            <div id="output" class="hidden mt-6 bg-slate-800 p-6 rounded-xl border border-slate-700">
                <div class="flex justify-between text-xs text-slate-400 mb-4">
                    <span id="statusBadge" class="text-emerald-400 font-bold"></span>
                    <span id="metaInfo"></span>
                </div>
                <h3 class="text-lg font-semibold mb-2 text-cyan-300">Extracted Intelligence:</h3>
                <ul id="list" class="list-disc pl-5 space-y-2 text-slate-200"></ul>
            </div>
        </div>

        <script>
            async function runScout() {
                const url = document.getElementById('url').value;
                const goal = document.getElementById('goal').value;
                const btn = document.getElementById('btn');
                const loading = document.getElementById('loading');
                const output = document.getElementById('output');
                
                btn.disabled = true;
                loading.classList.remove('hidden');
                output.classList.add('hidden');

                try {
                    const res = await fetch('/api/scout', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({url, goal})
                    });
                    const data = await res.json();
                    
                    document.getElementById('statusBadge').innerText = "STATUS: " + data.status;
                    document.getElementById('metaInfo').innerText = `Run ID: ${data.run_id || 'N/A'} | Steps: ${data.num_of_steps || 1}`;
                    
                    const list = document.getElementById('list');
                    list.innerHTML = '';
                    (data.extracted_data || []).forEach(item => {
                        const li = document.createElement('li');
                        li.innerText = item;
                        list.appendChild(li);
                    });
                    output.classList.remove('hidden');
                } catch (err) {
                    alert("Error running agent: " + err);
                } finally {
                    btn.disabled = false;
                    loading.classList.add('hidden');
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/scout")
async def scout_web(request: ScoutRequest):
    try:
        response = await client.agent.run(
            url=request.url,
            goal=request.goal
        )
        raw_text = ""
        if hasattr(response, 'result') and isinstance(response.result, dict):
            raw_text = response.result.get('result', '')
        elif hasattr(response, 'result'):
            raw_text = str(response.result)
        else:
            raw_text = str(response)

        cleaned_items = [item.strip() for item in raw_text.split('\n') if item.strip()]

        return {
            "status": getattr(response, "status", "COMPLETED"),
            "run_id": getattr(response, "run_id", None),
            "num_of_steps": getattr(response, "num_of_steps", None),
            "url": request.url,
            "goal": request.goal,
            "result": getattr(response, "result", raw_text),
            "extracted_data": cleaned_items,
            "error": getattr(response, "error", None)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
