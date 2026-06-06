"""
End2End Quality Assurance · GEN AI  —  Streamlit front-end
=========================================================
A re-skinned, restructured version of the original QA Automation Agent app.

What changed vs. the original
-----------------------------
• Light, AI-forward "Aurora" theme (Manrope / Space Grotesk / JetBrains Mono)
• A guided 4-step progress rail (Upload → Run → Review → Results)
• The 4 final artifacts are shown in TOP TABS instead of a sidebar radio
• A cleaner upload card, run panel, and human-review block
• Same backend wiring: build_graph(), agent.invoke(), Command(resume=...),
  session_state machinery and the human-in-the-loop interrupt are untouched.

Pair this with the provided .streamlit/config.toml.
"""

import os
import sys
import uuid
import pandas as pd
import streamlit as st
from langgraph.types import Command

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Backend.graph import build_graph


# ----------------------------------------------------------------------
# Page config  (must be the first Streamlit call)
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="End2End QA · GEN AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
OUTPUT_DIR = "Output"


def load_markdown_file(file_name: str) -> str:
    path = os.path.join(OUTPUT_DIR, file_name)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"File not found: {path}")
        return ""
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return ""


def reset_session():
    st.session_state.result = None
    st.session_state.waiting_for_approval = False
    st.session_state.file_path = None
    st.session_state.interrupt_counter = 0
    st.session_state.error = None
    st.session_state.thread_id = str(uuid.uuid4())


# ----------------------------------------------------------------------
# Session state init
# ----------------------------------------------------------------------
agent = build_graph()

_defaults = {
    "thread_id": str(uuid.uuid4()),
    "result": None,
    "waiting_for_approval": False,
    "file_path": None,
    "interrupt_counter": 0,
    "error": None,
}
for k, v in _defaults.items():
    st.session_state.setdefault(k, v)

config = {"configurable": {"thread_id": st.session_state.thread_id}}


# ----------------------------------------------------------------------
# Global styles  (the "Aurora" look, adapted to Streamlit's DOM)
# ----------------------------------------------------------------------
st.markdown(
    """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
:root{
  --accent:#44464E; --accent-ink:#303239; --accent-soft:#EDEDEF; --accent-soft2:#E2E2E6;
  --grad:linear-gradient(120deg,#3F414A,#303239);
  --text:#2A2B2F; --text-2:#54565E; --text-3:#76787F; --text-4:#9A9CA3;
  --border:#E4E4E7; --border-2:#D6D6DB; --hairline:#EDEDEF;
  --surface:#FFFFFF; --surface-2:#FAFAFB; --surface-3:#F1F1F3;
  --green:#1F9D6B; --green-soft:#E7F6EF; --red:#D6453C; --red-soft:#FBECEB;
  --amber:#C98A1E; --amber-soft:#FBF1DF;
}

/* fonts */
html, body, [class*="css"], .stMarkdown, p, span, label, div { font-family:'Manrope',system-ui,sans-serif; }
h1,h2,h3,h4{ font-family:'Space Grotesk',system-ui,sans-serif; letter-spacing:-.01em; color:var(--text); }

/* page canvas */
.stApp{ background:
  radial-gradient(1100px 640px at 86% -8%, #F2F2F4, transparent 60%),
  radial-gradient(900px 560px at -6% 6%, #EFEFF1, transparent 58%),
  #F8F8F9; }
.block-container{ max-width:1100px; padding-top:1.6rem; padding-bottom:5rem; }
header[data-testid="stHeader"]{ background:transparent; }
#MainMenu, footer{ visibility:hidden; }

/* ---------- custom header ---------- */
.e2e-top{ display:flex; align-items:center; gap:14px; padding:6px 2px 22px; }
.e2e-mark{ width:40px; height:40px; border-radius:8px; background:var(--grad);
  display:grid; place-items:center; box-shadow:0 6px 16px rgba(48,50,57,.24);
  color:#fff; font-size:19px; flex-shrink:0; }
.e2e-name{ font-family:'Space Grotesk'; font-weight:600; font-size:18px; color:var(--text);
  display:flex; align-items:center; gap:10px; line-height:1; }
.e2e-sub{ font-size:11.5px; color:var(--text-3); margin-top:3px; font-weight:500; letter-spacing:.03em; }
.e2e-badge{ font-family:'JetBrains Mono'; font-size:9.5px; font-weight:600; letter-spacing:.12em;
  text-transform:uppercase; padding:3px 8px 2px; border-radius:999px; color:var(--accent-ink);
  background:var(--accent-soft); border:1px solid var(--accent-soft2); }

/* ---------- progress rail ---------- */
.rail{ display:flex; gap:6px; background:var(--surface); border:1px solid var(--border);
  border-radius:10px; padding:8px; box-shadow:0 2px 14px rgba(40,42,48,.05); margin-bottom:26px; }
.rail-step{ flex:1; display:flex; align-items:center; gap:11px; padding:10px 14px; border-radius:6px; }
.rail-step.active{ background:var(--accent-soft); }
.rail-num{ width:27px; height:27px; border-radius:5px; display:grid; place-items:center;
  font-family:'JetBrains Mono'; font-size:12px; font-weight:600; background:var(--surface-3);
  color:var(--text-3); border:1px solid var(--border); flex-shrink:0; }
.rail-step.active .rail-num{ background:var(--grad); color:#fff; border-color:transparent;
  box-shadow:0 4px 12px rgba(48,50,57,.28); }
.rail-step.done .rail-num{ background:var(--green-soft); color:var(--green);
  border-color:rgba(31,157,107,.25); }
.rail-k{ font-size:9.5px; font-weight:700; letter-spacing:.09em; text-transform:uppercase; color:var(--text-4); }
.rail-t{ font-size:13.5px; font-weight:600; color:var(--text-2); }
.rail-step.active .rail-t{ color:var(--accent-ink); }
.rail-sep{ display:grid; place-items:center; color:var(--border-2); font-size:15px; }

/* ---------- section headers ---------- */
.eyebrow{ font-family:'JetBrains Mono'; font-size:11px; font-weight:600; letter-spacing:.12em;
  text-transform:uppercase; color:var(--accent); margin-bottom:8px; }
.step-title{ font-size:30px; font-weight:600; margin:0 0 8px; }
.step-lede{ font-size:15px; color:var(--text-2); line-height:1.55; max-width:62ch; margin-bottom:6px; }

/* ---------- buttons ---------- */
div.stButton > button, div.stDownloadButton > button{
  font-family:'Manrope'; font-weight:600; font-size:14.5px; border:none; border-radius:6px;
  padding:.66rem 1.4rem; color:#fff; background:var(--grad);
  box-shadow:0 6px 16px rgba(48,50,57,.22), inset 0 1px 0 rgba(255,255,255,.12);
  transition:transform .12s ease, filter .2s ease, box-shadow .2s ease; }
div.stButton > button:hover, div.stDownloadButton > button:hover{
  filter:brightness(1.12); transform:translateY(-1px); color:#fff;
  box-shadow:0 14px 30px rgba(48,50,57,.26); }
div.stButton > button:active{ transform:translateY(0); }
div.stButton > button:disabled{ background:var(--surface-3); color:var(--text-4); box-shadow:none; }
/* secondary buttons */
div.stButton > button[kind="secondary"]{ background:var(--surface); color:var(--text-2);
  border:1px solid var(--border); box-shadow:0 1px 2px rgba(80,60,140,.05); }
div.stButton > button[kind="secondary"]:hover{ color:var(--text); border-color:var(--border-2); }

/* ---------- file uploader ---------- */
div[data-testid="stFileUploader"] section{ border:1.6px dashed var(--border-2); border-radius:8px;
  background:var(--surface-2); padding:26px; transition:all .2s ease; }
div[data-testid="stFileUploader"] section:hover{ border-color:var(--accent); background:var(--accent-soft); }
div[data-testid="stFileUploader"] section small{ color:var(--text-3); }

/* ---------- tabs (the 4 artifacts) ---------- */
button[data-baseweb="tab"]{ font-family:'Manrope'; font-weight:600; font-size:13.5px;
  color:var(--text-3); border-radius:5px; padding:9px 16px; }
button[data-baseweb="tab"]:hover{ color:var(--text); }
button[data-baseweb="tab"][aria-selected="true"]{ color:var(--accent-ink); background:var(--surface); }
div[data-baseweb="tab-list"]{ gap:4px; background:var(--surface-3); border:1px solid var(--border);
  border-radius:8px; padding:5px; }
div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"]{ background:transparent !important; }

/* ---------- radio (decision) ---------- */
div[data-testid="stRadio"] label{ font-weight:600; color:var(--text-2); }
div[data-testid="stRadio"] label:hover{ color:var(--accent-ink); }

/* ---------- dataframe ---------- */
div[data-testid="stDataFrame"]{ border-radius:8px; overflow:hidden;
  border:1px solid var(--border); box-shadow:0 1px 2px rgba(40,42,48,.05); }

/* ---------- alerts / status ---------- */
div[data-testid="stNotification"], div[data-baseweb="notification"]{ border-radius:13px; }
div[data-testid="stExpander"]{ border-radius:13px; border:1px solid var(--border); }

/* ---------- stat cards ---------- */
.statgrid{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:6px 0 22px; }
.stat{ background:var(--surface-2); border:1px solid var(--border); border-radius:8px; padding:15px 18px; }
.stat-v{ font-family:'Space Grotesk'; font-weight:600; font-size:26px; color:var(--text); line-height:1; }
.stat-k{ font-size:11.5px; color:var(--text-3); margin-top:6px; font-weight:600; }
.result-banner{ display:flex; align-items:center; gap:14px; padding:16px 20px; margin-bottom:20px;
  background:linear-gradient(135deg,#F3F3F5,#EEEEF0); border:1px solid var(--accent-soft2); border-radius:10px; }
.rb-ico{ width:40px; height:40px; border-radius:8px; background:#fff; border:1px solid var(--accent-soft2);
  display:grid; place-items:center; color:var(--green); font-size:20px; }
.rb-t{ font-family:'Space Grotesk'; font-weight:600; font-size:16px; color:var(--text); }
.rb-s{ font-size:13px; color:var(--text-2); margin-top:2px; }
</style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------
# Custom header
# ----------------------------------------------------------------------
st.markdown(
    """
<div class="e2e-top">
  <div class="e2e-mark">🛡️</div>
  <div>
    <div class="e2e-name">End2End Quality Assurance
      <span class="e2e-badge">● GEN AI</span></div>
    <div class="e2e-sub">AI-POWERED E2E TEST AGENT</div>
  </div>
</div>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------
# Progress rail  (computed from session state)
# ----------------------------------------------------------------------
def current_step() -> int:
    if st.session_state.result is None:
        return 0                                  # Upload / Run
    if st.session_state.waiting_for_approval:
        return 2                                  # Human review
    return 3                                       # Results


def render_rail(active: int):
    steps = [("Step 1", "Upload"), ("Step 2", "Run agent"),
             ("Step 3", "Human review"), ("Step 4", "Results")]
    html = ['<div class="rail">']
    for i, (k, t) in enumerate(steps):
        state = "done" if i < active else "active" if i == active else ""
        num = "✓" if i < active else f"{i+1:02d}"
        html.append(
            f'<div class="rail-step {state}"><div class="rail-num">{num}</div>'
            f'<div><div class="rail-k">{k}</div><div class="rail-t">{t}</div></div></div>'
        )
        if i < 3:
            html.append('<div class="rail-sep">›</div>')
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


render_rail(current_step())


# ----------------------------------------------------------------------
# STEP 1 — Upload
# ----------------------------------------------------------------------
if st.session_state.result is None:
    st.markdown(
        '<div class="eyebrow">Step 1 · Source document</div>'
        '<div class="step-title">Upload your design document</div>'
        '<div class="step-lede">Drop a PDF or Word design spec. The agent reads it end-to-end, '
        'extracts requirements, and authors a complete test suite — you stay in control with a '
        'review checkpoint before anything is finalized.</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader("Upload design document", type=["pdf", "docx"],
                                     label_visibility="collapsed")

    # Reset when the file is removed
    if uploaded_file is None and st.session_state.file_path is not None:
        reset_session()
        st.rerun()

    if uploaded_file and not st.session_state.file_path:
        os.makedirs("designs", exist_ok=True)
        file_path = os.path.join("designs", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        st.session_state.file_path = file_path
        st.success(f"**{uploaded_file.name}** uploaded. Click **Run QA agent** to begin.")

    if st.session_state.file_path:
        st.info(
            "The agent will run **three stages**: requirement analysis and test-plan generation "
            "happen **in parallel**, then it authors detailed test cases and **pauses for your "
            "review**. After you approve, the traceability matrix is produced automatically."
        )

    # ----- STEP 2 — Run -----
    run_disabled = not st.session_state.file_path or st.session_state.waiting_for_approval

    c1, c2 = st.columns([3, 1])
    with c2:
        run = st.button("▶  Run QA agent", disabled=run_disabled, use_container_width=True)

    if run:
        st.session_state.error = None
        with st.status("Running the QA agent pipeline…", expanded=True) as status:
            st.write("Extracting text from the design document…")
            st.write("Analyzing requirements & generating the test plan (in parallel)…")
            st.write("Authoring detailed test cases…")
            try:
                result = agent.invoke({"file_path": st.session_state.file_path}, config=config)
                st.session_state.result = result
                if "__interrupt__" in result:
                    st.session_state.waiting_for_approval = True
                    status.update(label="Test cases generated — your review is needed.", state="complete")
                else:
                    st.session_state.waiting_for_approval = False
                    status.update(label="Pipeline complete!", state="complete")
                st.rerun()
            except Exception as e:
                st.session_state.error = str(e)
                status.update(label="Pipeline failed — see the error below.", state="error")

    if st.session_state.error:
        st.error(f"**Pipeline error**\n\n{st.session_state.error}")
        st.warning("Fix the issue above (e.g. API key or network) and click **Run QA agent** to retry.")


# ----------------------------------------------------------------------
# STEP 3 — Human review (interrupt)
# ----------------------------------------------------------------------
elif st.session_state.waiting_for_approval:
    interrupt_id = st.session_state.get("interrupt_counter", 0)
    interrupt_data = st.session_state.result["__interrupt__"][0].value

    st.markdown(
        '<div class="eyebrow">Step 3 · Human-in-the-loop</div>'
        '<div class="step-title">Review the generated test cases</div>'
        '<div class="step-lede">The agent paused here on purpose. Inspect the suite below, then '
        'approve to build the traceability matrix — or reject with feedback and the agent will '
        'regenerate.</div>',
        unsafe_allow_html=True,
    )

    df = pd.read_csv(interrupt_data["testcases"])
    st.dataframe(df, use_container_width=True, height=460)

    st.markdown('<div class="eyebrow" style="margin-top:18px">Your decision</div>',
                unsafe_allow_html=True)
    decision = st.radio("Your decision", ["Approve", "Reject"],
                        key=f"decision_{interrupt_id}", horizontal=True,
                        label_visibility="collapsed")

    feedback = ""
    if decision == "Reject":
        st.warning("Describe what needs to change so the agent can regenerate the test cases.")
        feedback = st.text_area("Feedback for the agent", key=f"feedback_{interrupt_id}",
                                placeholder="e.g. Add boundary cases for promo-code stacking, and a "
                                            "negative case for an expired card during a network retry…")

    submit_disabled = decision == "Reject" and not feedback.strip()

    c1, c2 = st.columns([3, 1])
    with c2:
        submit = st.button("Submit decision", key=f"btn_{interrupt_id}",
                           disabled=submit_disabled, use_container_width=True)

    if submit:
        resume_data = ({"status": "approved", "feedback": ""} if decision == "Approve"
                       else {"status": "rejected", "feedback": feedback})
        spinner_msg = ("Building the traceability matrix…" if decision == "Approve"
                       else "Regenerating test cases with your feedback…")
        with st.spinner(spinner_msg):
            try:
                result = agent.invoke(Command(resume=resume_data), config=config)
                st.session_state.result = result
                st.session_state.error = None
                if "__interrupt__" in result:
                    st.session_state.waiting_for_approval = True
                    st.session_state.interrupt_counter = interrupt_id + 1
                else:
                    st.session_state.waiting_for_approval = False
                    st.session_state.interrupt_counter = 0
            except Exception as e:
                st.session_state.error = str(e)
                st.session_state.waiting_for_approval = False
        st.rerun()


# ----------------------------------------------------------------------
# STEP 4 — Results (top tabs)
# ----------------------------------------------------------------------
else:
    result = st.session_state.result

    st.markdown(
        '<div class="result-banner"><div class="rb-ico">✓</div><div>'
        '<div class="rb-t">All artifacts generated &amp; approved</div>'
        '<div class="rb-s">Use the tabs below to explore the outputs, or start a new run.</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    cols = st.columns([1, 1, 1, 1, 1.2])
    with cols[4]:
        if st.button("↻  New run", use_container_width=True):
            reset_session()
            st.rerun()

    tab_req, tab_plan, tab_cases, tab_trace = st.tabs(
        ["📄  Requirement Analysis", "🧪  Test Plan", "📋  Test Cases", "🔗  Traceability Matrix"]
    )

    with tab_req:
        md = load_markdown_file("requirement_analysis.md")
        if md:
            st.markdown(md, unsafe_allow_html=True)

    with tab_plan:
        md = load_markdown_file("test_plan.md")
        if md:
            st.markdown(md, unsafe_allow_html=True)

    with tab_cases:
        if result.get("test_case_path"):
            df = pd.read_csv(result["test_case_path"])
            st.dataframe(df, use_container_width=True, height=520)

    with tab_trace:
        md = load_markdown_file("traceability_matrix.md")
        if md:
            st.markdown(md, unsafe_allow_html=True)
