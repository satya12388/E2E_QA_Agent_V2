from Backend.Utils.get_model import get_model
from Backend.Utils.markdown_converter import convert_to_md
from Backend.Schemas.test_plan_schema import TestPlan
from Backend.Prompts.test_plan_template import test_plan_template

from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()
model = get_model()
strc_model = model.with_structured_output(TestPlan)

prompt = PromptTemplate(
    template=test_plan_template,
    input_variables=['requirements']
)


def f_test_plan(state):
    requirements = state['requirement_analysis']
    chain = prompt | strc_model
    try:
        result = chain.invoke({'requirements': requirements})
    except Exception as e:
        raise RuntimeError(f"Test plan generation failed: {e}") from e
    convert_to_md(result, 'test_plan.md')
    return {"test_plan": result}

    