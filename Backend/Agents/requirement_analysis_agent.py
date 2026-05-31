from Backend.Utils.get_model import get_model
from Backend.Utils.document_loader import load_document
from Backend.Utils.markdown_converter import convert_to_md
from Backend.Schemas.requirement_schema import RequirementAnalysis
from Backend.Prompts.requirement_template import requirement_template
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv


load_dotenv()
model = get_model()
strc_model = model.with_structured_output(RequirementAnalysis)

prompt = PromptTemplate(
    template=requirement_template,
    input_variables=['raw_text']
)


def f_extract_requirements(state):
    file_path = state['file_path']
    raw_text = load_document(file_path)
    chain = prompt | strc_model
    try:
        result = chain.invoke({'raw_text': raw_text})
    except Exception as e:
        raise RuntimeError(f"Requirement analysis failed: {e}") from e
    convert_to_md(result, 'requirement_analysis.md')
    return {"raw_design_text": raw_text, "requirement_analysis": result}

    