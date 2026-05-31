# E2E QA Agent — Codebase Reference

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
│   ├── requirement_analysis.md
│   ├── test_plan.md
│   ├── test_cases.csv
│   └── traceability_matrix.md
├── designs/                 # Design document inputs (PDF/DOCX uploads land here)
│   ├── ParaBank_Enterprise_DDD.pdf
│   └── SauceDemo_Enterprise_Design_v2.pdf
├── main.py                  # Placeholder entry point (not used by the app)
├── pyproject.toml           # Project metadata and dependencies (uv-managed)
├── requirements.txt         # Flat pip requirements list
├── .env                     # API keys (GROQ_API_KEY, GOOGLE_API_KEY, SARVAM_API_KEY)
├── .streamlit/config.toml   # Streamlit dark terminal theme
└── .python-version          # Python 3.12
```

---

## Key Components

### `Backend/graph.py` — Pipeline Orchestration

Defines `QAState` (TypedDict) and builds the LangGraph `StateGraph`. Key state fields:

| Field | Type | Purpose |
|---|---|---|
| `file_path` | str | Path to uploaded design doc |
| `raw_design_text` | str | Extracted text from doc |
| `requirement_analysis` | RequirementAnalysis | Structured requirements |
| `test_plan` | TestPlan | Generated test plan |
| `test_cases` | TestSuite | Generated test cases |
| `test_case_path` | str | Path to saved CSV (`Output/test_cases.csv`) |
| `traceability` | TraceabilityMatrix | RTM |
| `approval_status` | str | `"approved"` or `"rejected"` |
| `feedback` | str | Human feedback on rejection |

`InMemorySaver` checkpointer enables the human interrupt/resume pattern.

### `Backend/Utils/get_model.py` — LLM Factory

`get_model(provider, temperature)` — default provider is `"groq"` using `qwen/qwen3-32b`.

| Provider key | Model |
|---|---|
| `"groq"` | qwen/qwen3-32b via Groq API |
| `"google"` | gemini-2.5-flash via Google GenAI |
| `"ollama"` | gemma4:e2b via local Ollama |
| `"ollamaBrowser"` | gemma4:e2b via browser-use's ChatOllama |
| `"sarvam"` | Sarvam 105b |

All agents use `get_model()` (defaults to `"groq"`) and call `.with_structured_output(Schema)`.

### `Backend/Utils/mardown_converter.py`

Calls the LLM a second time with `markdown_template` to convert any Pydantic structured object into clean Markdown, then writes to `Output/<file_name>`.

### `Backend/Utils/csv_convertor.py`

Flattens `TestSuite` into a CSV where each row is one `TestStep`. Columns: `TestCaseID`, `RequirementID`, `Title`, `Preconditions`, `StepNumber`, `Action`, `ExpectedResult`, `Priority`, `agent_instructions`.

### `Frontend/app.py` — Streamlit UI

- Uploads design doc → saves to `designs/`
- Invokes graph → handles `__interrupt__` pause for human review
- Shows CSV of test cases with Approve/Reject radio + feedback textarea
- On approval completion, shows sidebar navigation for all four output artifacts

---

## Running the App

```bash
# Install dependencies
uv sync   # or: pip install -r requirements.txt

# Set up .env with API keys (already present, do not commit)

# Launch Streamlit
streamlit run Frontend/app.py
```

---

## Environment Variables (`.env`)

| Variable | Used by |
|---|---|
| `GROQ_API_KEY` | `ChatGroq` (default LLM provider) |
| `GOOGLE_API_KEY` | `ChatGoogleGenerativeAI` |
| `SARVAM_API_KEY` | `SarvamLLM` |

`.env` is not in `.gitignore` — **do not commit API keys to version control**.

---

## Output Files

All outputs write to `Output/`. The directory must exist before running.

| File | Format | Produced by |
|---|---|---|
| `requirement_analysis.md` | Markdown | `requirement_analysis_agent` → `mardown_converter` |
| `test_plan.md` | Markdown | `test_plan_agent` → `mardown_converter` |
| `test_cases.csv` | CSV | `test_case_agent` → `csv_convertor` |
| `traceability_matrix.md` | Markdown | `traceability_agent` → `mardown_converter` |

---

## Development Notes

- All Agents follow the same pattern: `prompt | model.with_structured_output(Schema)` → save to file → return state update.
- To add a new LLM provider, add a branch in `Backend/Utils/get_model.py`.
- To change the default model, change the `provider` default in `get_model()` or update the agent-level call.
- The `0.2.2` file at the root appears to be an empty version marker file.
