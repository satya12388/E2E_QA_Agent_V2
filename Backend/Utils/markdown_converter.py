from langchain_core.prompts import PromptTemplate
from Backend.Prompts.markdown_template import markdown_template
from Backend.Utils.get_model import get_model
from dotenv import load_dotenv
import os

load_dotenv()
model = get_model()

prompt = PromptTemplate(
    template=markdown_template,
    input_variables=['content']
)

def convert_to_md(content, file_name):
    chain = prompt | model
    try:
        result = chain.invoke({'content': content})
    except Exception as e:
        raise RuntimeError(f"Markdown conversion failed for {file_name}: {e}") from e
    os.makedirs("Output", exist_ok=True)
    path = 'Output/' + file_name
    with open(path, 'w', encoding='utf-8') as file:
        file.write(result.content)


    