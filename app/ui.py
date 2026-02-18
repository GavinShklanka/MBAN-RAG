from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import io
import contextlib
import html

from app.core.instrumentation import instrument_run
from app.rag.vanilla import run_vanilla_rag
from app.rag.agentic import run_agentic_rag

app = FastAPI()


# ---------------------------------------------------------
# Utility: Capture CLI Reasoning Output
# ---------------------------------------------------------

def capture_output(func, *args, **kwargs):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = func(*args, **kwargs)
    return result, buffer.getvalue()


# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home():
    return render_page()


@app.post("/", response_class=HTMLResponse)
async def query(
    question: str = Form(...),
    mode: str = Form(...)
):

    if mode == "vanilla":
        result, reasoning = capture_output(
            lambda q: instrument_run(run_vanilla_rag, q),
            question
        )
    else:
        result, reasoning = capture_output(
            lambda q: instrument_run(run_agentic_rag, q),
            question
        )

    return render_page(
        question=question,
        answer=result.get("answer", ""),
        reasoning=reasoning,
        mode=mode,
        coverage=result.get("coverage"),
        tokens=result.get("tokens"),
        latency=result.get("latency")
    )


# ---------------------------------------------------------
# Page Renderer
# ---------------------------------------------------------

def render_page(question="", answer="", reasoning="", mode="vanilla",
                coverage=None, tokens=None, latency=None):

    safe_question = html.escape(question)
    safe_answer = html.escape(answer)
    safe_reasoning = html.escape(reasoning)

    formatted_answer = safe_answer.replace("\n", "<br>")

    return f"""
<!DOCTYPE html>
<html>
<head>
<title>Clinical Retrieval System</title>

<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #f5f5f7;
    margin: 0;
    color: #1d1d1f;
}}

.container {{
    display: flex;
    max-width: 1200px;
    margin: 60px auto;
    gap: 40px;
}}

.panel {{
    background: white;
    padding: 40px;
    border-radius: 14px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.05);
    flex: 1;
}}

h1 {{
    font-weight: 500;
    margin-bottom: 10px;
}}

h2 {{
    margin-top: 40px;
    font-weight: 500;
}}

.subtitle {{
    color: #6e6e73;
    font-size: 14px;
    margin-top: -10px;
    margin-bottom: 20px;
}}

textarea {{
    width: 100%;
    padding: 14px;
    font-size: 14px;
    border-radius: 8px;
    border: 1px solid #d2d2d7;
    resize: vertical;
}}

select {{
    margin-top: 15px;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #d2d2d7;
}}

button {{
    margin-top: 15px;
    padding: 10px 18px;
    border-radius: 8px;
    border: none;
    background: #0071e3;
    color: white;
    font-weight: 500;
    cursor: pointer;
}}

button:hover {{
    background: #005bb5;
}}

.response {{
    margin-top: 20px;
    line-height: 1.6;
    font-size: 15px;
}}

pre {{
    white-space: pre-wrap;
    font-size: 13px;
    background: #f2f2f2;
    padding: 20px;
    border-radius: 10px;
    overflow-x: auto;
}}

.badges {{
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}}

.badge {{
    background: #e8f1ff;
    color: #0071e3;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 500;
}}
</style>

</head>
<body>

<div class="container">

    <!-- LEFT PANEL -->
    <div class="panel">

        <h1>User Query</h1>

        <p class="subtitle">
        Clinical question-answering system with transparent retrieval reasoning.
        </p>

        <details style="margin-bottom:20px;">
            <summary style="cursor:pointer; font-weight:500; color:#0071e3;">
                Example Prompts (Click to Expand)
            </summary>
            <div style="margin-top:15px; font-size:14px; line-height:1.6;">
                <b>Multi-condition:</b><br>
                • bipolar disorder and insomnia<br>
                • diabetes and depression<br><br>

                <b>DSM-style:</b><br>
                • major depressive disorder and generalized anxiety disorder<br><br>

                <b>Single-condition:</b><br>
                • borderline personality disorder<br>
                • schizophrenia treatment options<br><br>

                <b>When to seek help:</b><br>
                • warning signs of suicidal ideation<br>
            </div>
        </details>

        <form method="post">
            <textarea name="question" rows="4">{safe_question}</textarea>
            <br>
            <select name="mode">
                <option value="vanilla" {"selected" if mode=="vanilla" else ""}>
                    Vanilla RAG
                </option>
                <option value="agentic" {"selected" if mode=="agentic" else ""}>
                    Agentic RAG
                </option>
            </select>
            <br>
            <button type="submit">Submit</button>
        </form>

        <h2>Response</h2>

        <div class="response">
            {formatted_answer}
        </div>

    </div>


    <!-- RIGHT PANEL -->
    <div class="panel">

        <h1>System Reasoning</h1>

        <div class="badges">
            {f'<div class="badge">Coverage: {round(coverage*100,1)}%</div>' if coverage is not None else ''}
            {f'<div class="badge">Tokens: {tokens}</div>' if tokens is not None else ''}
            {f'<div class="badge">Latency: {latency:.2f}s</div>' if latency is not None else ''}
        </div>

        <pre>{safe_reasoning}</pre>

    </div>

</div>

</body>
</html>
"""
