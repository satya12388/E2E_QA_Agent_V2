# E2E QA Agent

## What This Project Does

An AI-powered, end-to-end QA automation system that takes a software design document (PDF/DOCX) and autonomously produces:

1. **Requirement Analysis** — structured list of requirements extracted from the design doc
2. **Test Plan** — professional test plan based on those requirements
3. **Test Cases** — detailed, step-by-step test cases mapped to requirements
4. **Traceability Matrix** — RTM linking each requirement to its test cases with coverage metrics

The system includes a **human-in-the-loop review step**: after test cases are generated, a human must approve or reject them (with feedback). On rejection the test cases are regenerated incorporating the feedback; on approval the traceability matrix is produced.

---

## Architecture

```
Design Doc (PDF/DOCX)
        │
        ▼
┌───────────────────────┐
│  LangGraph State Graph │  (Backend/graph.py)
│                       │
│  n_requirement_analysis ──► n_test_plan ──► END
│         │
│         ▼
│     n_test_cases
│         │
│         ▼
│      n_review  ◄── Human interrupt (approve/reject with feedback)
│         │
│   ┌─────┴──────┐
│ approved     rejected
│   │              │
│   ▼              ▼
│ n_traceability  n_test_cases (regenerate with feedback)
│   │
│   ▼
│  END
└───────────────────────┘
        │
        ▼
  Streamlit UI (Frontend/app.py)
```

The graph runs `n_requirement_analysis` and `n_test_plan` in parallel from START (both depend only on `raw_design_text`). `n_test_cases` also starts from `n_requirement_analysis`.

---

## Project Structure

```
E2E_QA_Agent/
├── Frontend/
│   └── app.py               # Streamlit UI — file upload, graph execution, review UI, output viewer
├── Backend/
│   ├── graph.py             # LangGraph StateGraph definition and QAState schema
│   ├── Agents/              # LangGraph node functions (one per pipeline stage)
│   │   ├── requirement_analysis_agent.py
│   │   ├── test_plan_agent.py
│   │   ├── test_case_agent.py
│   │   ├── review_agent.py
│   │   └── traceability_agent.py
│   ├── Prompts/             # LangChain PromptTemplates (string templates)
│   │   ├── requirement_template.py
│   │   ├── test_plan_template.py
│   │   ├── test_cases_template.py
│   │   ├── traceability_template.py
│   │   └── markdown_template.py
│   ├── Schemas/             # Pydantic models for structured LLM output
│   │   ├── requirement_schema.py    # RequirementAnalysis, Requirement
│   │   ├── test_plan_schema.py      # TestPlan (complex nested model)
│   │   ├── test_cases_schema.py     # TestSuite, TestCase, TestStep
│   │   └── traceability_schema.py   # TraceabilityMatrix, TraceabilityEntry, RTMMetrics
│   └── Utils/               # Shared utility functions
│       ├── get_model.py         # LLM provider factory (groq/ollama/google/sarvam)
│       ├── document_loader.py   # PDF and DOCX text extraction
│       ├── mardown_converter.py # Converts structured output → Markdown file via LLM
│       └── csv_convertor.py     # Converts TestSuite → CSV (one row per test step)
├── Output/                  # Generated artifacts (git-ignored at runtime)
├── designs/                 # Design document inputs (PDF/DOCX uploads land here)
├── main.py                  # Placeholder entry point (not used by the app)
├── pyproject.toml           # Project metadata and dependencies (uv-managed)
├── requirements.txt         # Flat pip requirements list
├── .env                     # API keys (GROQ_API_KEY, GOOGLE_API_KEY, SARVAM_API_KEY)
├── .streamlit/config.toml   # Streamlit dark terminal theme
└── .python-version          # Python 3.12
```

### Note: use `CLAUDE.md` and `.claude` folder if developing using claude code, if not these could be ignored.

---

## Running the App

```bash
# Install dependencies
uv sync   # or: pip install -r requirements.txt

# Set up .env with API keys

# Launch Streamlit
streamlit run Frontend/app.py
```

---
