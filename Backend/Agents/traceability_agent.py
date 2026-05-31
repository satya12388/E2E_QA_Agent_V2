from Backend.Utils.markdown_converter import convert_to_md
from Backend.Schemas.traceability_schema import TraceabilityMatrix
from Backend.Prompts.traceability_template import traceability_template
from Backend.Utils.get_model import get_model
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()
model = get_model()
strc_model = model.with_structured_output(TraceabilityMatrix)

prompt = PromptTemplate(
    template=traceability_template,
    input_variables=['requirements','testcases']
)


def f_traceability(state):
    requirements = state['requirement_analysis']
    testcases = state['test_cases']
    chain = prompt | strc_model
    try:
        result = chain.invoke({'requirements': requirements, 'testcases': testcases})
    except Exception as e:
        raise RuntimeError(f"Traceability matrix generation failed: {e}") from e
    convert_to_md(result, 'traceability_matrix.md')
    return {"traceability": result}

    