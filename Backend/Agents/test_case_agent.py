from Backend.Schemas.test_cases_schema import TestSuite
from Backend.Prompts.test_cases_template import test_cases_template
from Backend.Utils.get_model import get_model
from Backend.Utils.csv_convertor import convert_to_csv
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv


load_dotenv()
model = get_model()
strc_model = model.with_structured_output(TestSuite)

prompt = PromptTemplate(
    template=test_cases_template,
    input_variables=['requirements','feedback']
)


def f_test_cases(state):
    requirements = state['requirement_analysis']
    feedback = state.get('feedback', '')
    chain = prompt | strc_model
    try:
        result = chain.invoke({'requirements': requirements, 'feedback': feedback})
    except Exception as e:
        raise RuntimeError(f"Test case generation failed: {e}") from e
    convert_to_csv(result, 'test_cases.csv')
    return {"test_cases": result, 'test_case_path': 'Output/test_cases.csv'}

    