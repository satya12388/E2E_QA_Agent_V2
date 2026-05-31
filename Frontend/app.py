import streamlit as st
import os, sys, uuid
import pandas as pd
from langgraph.types import Command

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Backend.graph import build_graph


# Function to load a Markdown file
def load_markdown_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
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


# Init graph
agent = build_graph()

# Session state init
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "result" not in st.session_state:
    st.session_state.result = None

if "waiting_for_approval" not in st.session_state:
    st.session_state.waiting_for_approval = False

if "file_path" not in st.session_state:
    st.session_state.file_path = None

if "interrupt_counter" not in st.session_state:
    st.session_state.interrupt_counter = 0

if "error" not in st.session_state:
    st.session_state.error = None

config = {"configurable": {"thread_id": st.session_state.thread_id}}


st.set_page_config(
    page_title="One Stop Shop for QA...",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* Primary buttons */
div.stButton > button {
    background-color: #A855F7;
    color: #FAFAFA;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.25rem;
    font-weight: 600;
    transition: background-color 0.2s ease, box-shadow 0.2s ease;
}
div.stButton > button:hover {
    background-color: #9333EA;
    box-shadow: 0 0 12px rgba(168, 85, 247, 0.5);
    color: #FAFAFA;
}
div.stButton > button:active {
    background-color: #7E22CE;
}

/* File uploader */
div[data-testid="stFileUploader"] section {
    border: 1.5px dashed #A855F7;
    border-radius: 10px;
    background-color: #18181B;
}
div[data-testid="stFileUploader"] section:hover {
    border-color: #C084FC;
    background-color: #1F1F27;
}

/* Radio buttons */
div[data-testid="stRadio"] label:hover {
    color: #C084FC;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111113;
    border-right: 1px solid #27272A;
}

/* Dataframe */
div[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #27272A;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
# QA Automation Agent Dashboard
### AI-powered E2E Test Agent
""")

# Upload Design File
st.markdown("**Step 1 — Upload your design document** (PDF or DOC)")
uploaded_file = st.file_uploader("Upload Design Document", type=["pdf", "docx"])

# Reset session when file is removed
if uploaded_file is None and st.session_state.file_path is not None:
    reset_session()
    st.rerun()

if uploaded_file and not st.session_state.file_path:
    os.makedirs("designs", exist_ok=True)

    file_path = os.path.join("designs", uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.session_state.file_path = file_path
    st.success(f"Document **{uploaded_file.name}** uploaded successfully. Click **Run QA Agent** to begin.")

if st.session_state.file_path and not st.session_state.result:
    st.info(
        "The agent will run **3 stages in sequence**:\n\n"
        "1. Extract & analyze requirements from your document\n"
        "2. Generate a test plan (runs in parallel with step 1)\n"
        "3. Generate detailed test cases → pause for your review\n\n"
        "After you approve the test cases, the traceability matrix is produced automatically."
    )

# Run button is disabled when: no file uploaded, waiting for human review, or pipeline already complete
# An active error re-enables the button so the user can retry
run_disabled = (
    not st.session_state.file_path
    or st.session_state.waiting_for_approval
    or (
        st.session_state.result is not None
        and not st.session_state.waiting_for_approval
        and not st.session_state.error
    )
)

if st.button("Run QA Agent", disabled=run_disabled):
    if not st.session_state.file_path:
        st.warning("Please upload a design document first.")
    else:
        st.session_state.error = None
        with st.status("Running QA Agent pipeline...", expanded=True) as status:
            st.write("Extracting text from the design document...")
            st.write("Analyzing requirements and generating test plan in parallel...")
            st.write("Generating test cases from the extracted requirements...")
            try:
                result = agent.invoke(
                    {"file_path": st.session_state.file_path},
                    config=config
                )
                st.session_state.result = result
                if "__interrupt__" in result:
                    st.session_state.waiting_for_approval = True
                    status.update(label="Test cases generated — your review is needed.", state="complete")
                else:
                    st.session_state.waiting_for_approval = False
                    status.update(label="Pipeline complete!", state="complete")
            except Exception as e:
                st.session_state.error = str(e)
                status.update(label="Pipeline failed — see error below.", state="error")


# Error Display
if st.session_state.error:
    st.divider()
    st.error(f"**Pipeline error**\n\n{st.session_state.error}")
    st.warning("Fix the issue above (e.g. check your API key or network) and click **Run QA Agent** to try again.")

# Interrupt Handling
interrupt_id = st.session_state.get("interrupt_counter", 0)
if st.session_state.waiting_for_approval:

    interrupt_data = st.session_state.result["__interrupt__"][0].value

    st.divider()
    st.subheader("📋 Human Review — Step 4")
    st.info(
        "The AI has finished generating test cases. "
        "Please review the table below and decide whether to **approve** or **reject** them.\n\n"
        "- **Approve** — the agent will proceed to build the traceability matrix.\n"
        "- **Reject** — provide feedback and the agent will regenerate the test cases."
    )

    test_case_path = interrupt_data["testcases"]

    # Show CSV
    df = pd.read_csv(test_case_path)
    st.dataframe(df)

    decision = st.radio("Your decision:",
                        ["Approve", "Reject"],
                        key=f"decision_{interrupt_id}")

    feedback = ""
    if decision == "Reject":
        st.warning("Describe what needs to change so the agent can regenerate the test cases.")
        feedback = st.text_area("Feedback for the agent", key=f"feedback_{interrupt_id}")

    submit_disabled = decision == "Reject" and not feedback.strip()

    if st.button("Submit Decision", key=f"btn_{interrupt_id}", disabled=submit_disabled):

        if decision == "Approve":
            resume_data = {
                "status": "approved",
                "feedback": ""
            }
        else:
            resume_data = {
                "status": "rejected",
                "feedback": feedback
            }

        spinner_msg = (
            "Generating traceability matrix..." if decision == "Approve"
            else "Regenerating test cases with your feedback..."
        )

        with st.spinner(spinner_msg):
            try:
                result = agent.invoke(
                    Command(resume=resume_data),
                    config=config
                )
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


# ✅ Final Output
if st.session_state.result and not st.session_state.waiting_for_approval:

    result = st.session_state.result

    st.success("All 4 artifacts generated successfully. Use the sidebar to explore the outputs.")

    # Sidebar Navigation
    st.sidebar.title("📁 Outputs")

    selected_view = st.sidebar.radio(
        "Select File to View",
        [
            "Requirement Analysis",
            "Test Plan",
            "Test Cases",
            "Traceability Matrix"
        ],
        index=2
    )
    st.sidebar.markdown("---")
    st.sidebar.info("👤 QA Review Mode Enabled")

    # 📄 Requirement Analysis
    if selected_view == "Requirement Analysis":
        st.subheader("📄 Requirement Analysis")
        markdown_content = load_markdown_file(r"Output\requirement_analysis.md")
        if markdown_content:
            st.markdown(markdown_content, unsafe_allow_html=True)

    # 🧪 Test Plan
    elif selected_view == "Test Plan":
        st.subheader("🧪 Test Plan")
        markdown_content = load_markdown_file(r"Output\test_plan.md")
        if markdown_content:
            st.markdown(markdown_content, unsafe_allow_html=True)

    # 📋 Test Cases
    elif selected_view == "Test Cases":
        st.subheader("📋 Test Cases")
        if result.get("test_case_path"):
            df = pd.read_csv(result["test_case_path"])
            st.dataframe(df,width='stretch',height=500)

    # 🔗 Traceability Matrix
    elif selected_view == "Traceability Matrix":
        st.subheader("🔗 Traceability Matrix")
        markdown_content = load_markdown_file(r"Output\traceability_matrix.md")
        if markdown_content:
            st.markdown(markdown_content, unsafe_allow_html=True)