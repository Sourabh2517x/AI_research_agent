"""ResearchAI: Streamlit front end for the existing research pipeline."""

import html
import importlib
import os
import re
from urllib.parse import urlparse

import streamlit as st

st.set_page_config(page_title="ResearchAI", layout="centered")

VIEWS = [
    "Overview",
    "Search Sources",
    "Scraped Content",
    "Research Report",
    "Critic Evaluation",
]

STAGES = [
    "Searching the web",
    "Reading relevant sources",
    "Writing the report",
    "Evaluating the report",
]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap');

:root {
    --bg: #0F1218;
    --surface: #161B24;
    --border: #262D3A;
    --text: #E7E9EE;
    --muted: #8B94A5;
    --accent: #45B8AC;
}

.stApp {
    font-family: 'Geist', system-ui, sans-serif;
    background:
        radial-gradient(900px 420px at 50% -8%, rgba(69, 184, 172, 0.10), transparent 70%),
        var(--bg);
}
.block-container { max-width: 900px; padding-top: 2.5rem; padding-bottom: 4rem; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

/* header */
.hdr {
    display: flex; justify-content: space-between; align-items: flex-start;
    gap: 1rem; margin-bottom: 2.2rem;
}
.brand { font-size: 2rem; font-weight: 600; letter-spacing: -0.02em; line-height: 1.1; }
.tag { color: var(--muted); margin-top: 0.35rem; font-size: 1rem; }
.pill {
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.25rem 0.75rem; border: 1px solid var(--border); border-radius: 999px;
    background: var(--surface); color: var(--muted); font-size: 0.85rem; white-space: nowrap;
}
.dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent); }
.dot.busy { background: #D9A441; }
.dot.err { background: #E5645F; }

.res-topic { font-size: 1.5rem; font-weight: 600; letter-spacing: -0.015em; margin-bottom: 0.5rem; }

/* input */
[data-testid="stForm"] { border: none; padding: 0; }
[data-testid="InputInstructions"] { display: none; } 
.stTextInput [data-baseweb="input"] {
    background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
}
.stTextInput [data-baseweb="base-input"] { background: transparent; }
.stTextInput input { font-size: 1.05rem; padding: 0.95rem 1rem; font-family: 'Geist', sans-serif; }
.stTextInput [data-baseweb="input"]:focus-within {
    border-color: var(--accent); box-shadow: 0 0 0 3px rgba(69, 184, 172, 0.15);
}

/* buttons */
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primaryFormSubmit"] {
    background: var(--accent); border: none; border-radius: 10px; width: 100%;
    padding: 0.7rem 1rem; font-weight: 600;
}
[data-testid="stBaseButton-primary"] p,
[data-testid="stBaseButton-primaryFormSubmit"] p { color: #06201D; font-weight: 600; }
[data-testid="stBaseButton-primary"]:hover,
[data-testid="stBaseButton-primaryFormSubmit"]:hover { background: #5CCABF; }

[data-testid="stBaseButton-secondary"] {
    background: transparent; border: 1px solid var(--border); border-radius: 10px;
}
[data-testid="stBaseButton-secondary"]:hover { border-color: var(--accent); }
.st-key-suggestions button { width: 100%; justify-content: flex-start; text-align: left; }

/* cards */
[class*="st-key-card-"] {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 1.1rem 1.3rem;
}
[data-testid="stMetric"] {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 0.9rem 1.1rem;
}
[data-testid="stExpander"] { border: 1px solid var(--border); border-radius: 12px; background: var(--surface); }
[data-testid="stExpander"] details { border: none; }

.stages { margin: 0.4rem 0 0.9rem 1.1rem; padding: 0; color: var(--text); line-height: 1.9; }
.muted { color: var(--muted); font-size: 0.92rem; }

/* report reads better in a serif at a narrower measure */
.st-key-card-report { padding: 1.6rem 1.9rem; }
.st-key-card-report .stMarkdown { max-width: 68ch; }
.st-key-card-report .stMarkdown p,
.st-key-card-report .stMarkdown li {
    font-family: 'Newsreader', Georgia, serif; font-size: 1.1rem; line-height: 1.7;
}
.st-key-card-report h1 { font-size: 1.6rem; }
.st-key-card-report h2 { font-size: 1.3rem; }
.st-key-card-report h3 { font-size: 1.1rem; }

@media (max-width: 640px) {
    .hdr { flex-direction: column; }
    .brand { font-size: 1.7rem; }
    .st-key-card-report { padding: 1.2rem; }
}
</style>
"""


# ---------- loading the pipeline ----------
def load_pipeline():
    """Import run_research_pipeline from pipelines.py (or pipeline.py)."""
    for name in ("pipelines", "pipeline"):
        try:
            return importlib.import_module(name).run_research_pipeline
        except ModuleNotFoundError as exc:
            if exc.name != name:  # a missing dependency inside the module, not the module itself
                raise
    raise ModuleNotFoundError("Couldn't find pipelines.py or pipeline.py next to app.py.")


# ---------- helpers ----------
def as_text(value) -> str:
    """Gemini responses can be a string or a list of content blocks."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("type", "text") == "text":
                parts.append(item.get("text", ""))
        return "\n".join(p for p in parts if p)
    return str(value)


def md_safe(text: str) -> str:
    """Stop dollar signs in scraped text from being read as LaTeX."""
    return text.replace("$", "\\$")


def redact(message: str) -> str:
    for name, value in os.environ.items():
        if value and len(value) >= 8 and any(w in name.upper() for w in ("KEY", "TOKEN", "SECRET", "PASSWORD")):
            message = message.replace(value, "[hidden]")
    return message


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50] or "report"


def parse_sources(raw: str) -> list[dict]:
    """Split the web_search tool output (Title/URL/Snippet blocks) into sources."""
    sources = []
    for block in re.split(r"\n-{3,}\n", raw):
        url = re.search(r"URL:\s*(\S+)", block)
        if not url:
            continue
        title = re.search(r"Title:\s*(.+)", block)
        snippet = re.search(r"Snippet:\s*(.*)", block, re.S)
        sources.append(
            {
                "title": title.group(1).strip() if title else url.group(1),
                "url": url.group(1),
                "snippet": snippet.group(1).strip() if snippet else "",
            }
        )
    return sources


def parse_feedback(text: str):
    """Return (score, strengths, improvements, verdict); empty values if not found."""
    score = re.search(r"Score:\W*(\d+(?:\.\d+)?)\s*/\s*10", text, re.I)

    def grab(pattern):
        m = re.search(pattern, text, re.I | re.S)
        return m.group(1).strip().rstrip("*#").strip() if m else ""

    strengths = grab(r"Strengths\W{0,4}\s*(.*?)(?=Areas to Improve|One line verdict|\Z)")
    improve = grab(r"Areas to Improve\W{0,4}\s*(.*?)(?=One line verdict|\Z)")
    verdict = grab(r"One line verdict\W{0,4}\s*(.*)")
    return (score.group(1) if score else None), strengths, improve, verdict


def make_preview(report: str, limit: int = 700) -> str:
    paragraphs = [
        p.strip() for p in re.split(r"\n\s*\n", report.strip())
        if p.strip() and not p.lstrip().startswith("#")
    ]
    out = ""
    for p in paragraphs:
        if out and len(out) + len(p) > limit:
            break
        out += p + "\n\n"
    out = out.strip()
    if len(out) > limit:
        out = out[:limit].rsplit(" ", 1)[0] + "…"
    return out


# ---------- state ----------
st.session_state.setdefault("running", False)
st.session_state.setdefault("pending", None)
st.session_state.setdefault("result", None)
st.session_state.setdefault("result_topic", "")
st.session_state.setdefault("error", None)
st.session_state.setdefault("notice", None)
st.session_state.setdefault("view", "Overview")


def start_research():
    topic = st.session_state.get("topic_input", "").strip()
    if not topic:
        st.session_state.notice = "Enter a topic before starting."
        return
    st.session_state.update(
        pending=topic, running=True, error=None, notice=None, result=None, view="Overview"
    )


def start_suggestion(topic: str):
    st.session_state.topic_input = topic
    start_research()


def reset():
    st.session_state.update(result=None, result_topic="", error=None, notice=None, view="Overview")
    st.session_state.topic_input = ""


def go_to(view: str):
    st.session_state.view = view


# ---------- page pieces ----------
def render_header():
    if st.session_state.running:
        dot, label = "busy", "Researching"
    elif st.session_state.error:
        dot, label = "err", "Last run failed"
    else:
        dot, label = "", "Ready"
    st.markdown(
        f"""
        <div class="hdr">
          <div>
            <div class="brand">ResearchAI</div>
            <div class="tag">From web search to evidence-backed research.</div>
          </div>
          <div class="pill"><span class="dot {dot}"></span>{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_input(busy: bool):
    with st.form("research_form"):
        col_input, col_btn = st.columns([5, 1.4], vertical_alignment="center")
        col_input.text_input(
            "Research topic",
            key="topic_input",
            placeholder="What would you like to research today?",
            label_visibility="collapsed",
            disabled=busy,
        )
        with col_btn:
            st.form_submit_button("Start Research", type="primary", on_click=start_research, disabled=busy)


    if st.session_state.notice:
        st.warning(st.session_state.notice)
    if st.session_state.error:
        st.error(st.session_state.error)


def run_pipeline(run_research_pipeline):
    """Runs once per click: the click sets running=True, and this clears it before the rerun."""
    topic = st.session_state.pending
    stage_items = "".join(f"<li>{s}</li>" for s in STAGES)
    with st.container(key="card-progress"):
        st.markdown(
            f"""
            <div style="font-weight:600">Working on: {html.escape(topic)}</div>
            <ol class="stages">{stage_items}</ol>
            <div class="muted">The pipeline only reports back when it has finished, so individual
            stages aren't tracked live.</div>
            """,
            unsafe_allow_html=True,
        )
        with st.spinner("Running the research pipeline…"):
            try:
                result = run_research_pipeline(topic)
                if not isinstance(result, dict):
                    raise TypeError("The pipeline didn't return a dictionary.")
                st.session_state.result = result
                st.session_state.result_topic = topic
                st.session_state.error = None
            except Exception as exc:
                st.session_state.result = None
                st.session_state.error = (
                    "The research run failed. Check your API keys and internet connection, then try again.\n\n"
                    f"Details: {redact(f'{type(exc).__name__}: {exc}')}"
                )
    st.session_state.running = False
    st.rerun()


def view_overview(result: dict, report: str, sources: list[dict]):
    metrics = []
    if sources:
        metrics.append(("Sources found", str(len(sources))))
    if report.strip():
        metrics.append(("Report length", f"{len(report.split()):,} words"))
    score, *_ = parse_feedback(as_text(result.get("feedback")))
    if score:
        metrics.append(("Critic score", f"{score}/10"))
    if metrics:
        for col, (label, value) in zip(st.columns(len(metrics)), metrics):
            col.metric(label, value)

    with st.container(key="card-preview"):
        st.markdown("**Report preview**")
        preview = make_preview(report) if report.strip() else ""
        if preview:
            st.markdown(md_safe(preview))
        else:
            st.markdown('<span class="muted">The pipeline returned no report text.</span>', unsafe_allow_html=True)

    st.markdown('<div class="muted" style="margin:1rem 0 0.4rem">Jump to</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.button("Full report", key="go_report", on_click=go_to, args=("Research Report",))
    c2.button("Sources", key="go_sources", on_click=go_to, args=("Search Sources",))
    c3.button("Critic evaluation", key="go_critic", on_click=go_to, args=("Critic Evaluation",))


def view_sources(raw: str):
    if not raw.strip():
        st.info("The search step didn't return any sources.")
        return
    sources = parse_sources(raw)
    if not sources:
        st.info("Couldn't split the search output into separate sources, so it is shown as returned.")
        st.text(raw)
        return
    st.caption(f"{len(sources)} sources")
    for i, src in enumerate(sources):
        with st.expander(md_safe(src["title"]), expanded=(i == 0)):
            if src["url"].startswith(("http://", "https://")):
                host = urlparse(src["url"]).netloc.removeprefix("www.") or src["url"]
                st.markdown(f"[{host}]({src['url'].replace(')', '%29')})")
            else:
                st.text(src["url"])
            if src["snippet"]:
                st.markdown(md_safe(src["snippet"]))


def view_scraped(text: str):
    if not text.strip():
        st.info("The reading step didn't return any content.")
        return
    st.caption("Output of the reading step, as returned by the pipeline.")
    if len(text) <= 700:
        st.markdown(md_safe(text))
        return
    st.markdown(md_safe(text[:600].rsplit(" ", 1)[0] + "…"))
    with st.expander("Show full content"):
        st.markdown(md_safe(text))


def view_report(report: str, topic: str):
    if not report.strip():
        st.info("The pipeline returned no report.")
        return
    with st.container(key="card-report"):
        st.markdown(report)
    st.download_button(
        "Download report (.md)",
        data=report,
        file_name=f"{slugify(topic)}.md",
        mime="text/markdown",
    )


def view_critic(feedback: str):
    if not feedback.strip():
        st.info("The critic didn't return any feedback.")
        return
    score, strengths, improve, verdict = parse_feedback(feedback)
    if not (score or strengths or improve or verdict):
        st.markdown(feedback)
        return
    if score:
        st.metric("Score", f"{score}/10")
        st.progress(max(0.0, min(float(score) / 10, 1.0)))
    left, right = st.columns(2)
    if strengths:
        with left.container(key="card-strengths"):
            st.markdown("**Strengths**")
            st.markdown(md_safe(strengths))
    if improve:
        with right.container(key="card-improve"):
            st.markdown("**Areas to improve**")
            st.markdown(md_safe(improve))
    if verdict:
        with st.container(key="card-verdict"):
            st.markdown("**Verdict**")
            st.markdown(md_safe(verdict))


def render_results():
    result = st.session_state.result
    topic = st.session_state.result_topic
    report = as_text(result.get("report"))
    raw_sources = as_text(result.get("search_results"))
    scraped = as_text(result.get("scraped_content"))
    feedback = as_text(result.get("feedback"))

    top, action = st.columns([4, 1.2], vertical_alignment="center")
    top.markdown(
        f'<div class="res-topic">{html.escape(topic)}</div>'
        '<div class="pill"><span class="dot"></span>Completed</div>',
        unsafe_allow_html=True,
    )
    action.button("New Research", on_click=reset)

    st.write("")
    view = st.segmented_control("View", VIEWS, key="view", label_visibility="collapsed") or "Overview"
    st.write("")

    if view == "Overview":
        view_overview(result, report, parse_sources(raw_sources))
    elif view == "Search Sources":
        view_sources(raw_sources)
    elif view == "Scraped Content":
        view_scraped(scraped)
    elif view == "Research Report":
        view_report(report, topic)
    else:
        view_critic(feedback)


# ---------- app ----------
st.markdown(CSS, unsafe_allow_html=True)

try:
    run_research_pipeline = load_pipeline()
except Exception as exc:
    st.error(f"Couldn't load the research pipeline: {redact(str(exc))}")
    st.stop()

render_header()

if st.session_state.result is not None:
    render_results()
else:
    render_input(busy=st.session_state.running)
    if st.session_state.running:
        run_pipeline(run_research_pipeline)