from pypdf import PdfReader
import docx

def load_document(file_path:str) -> str:

    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text+=page.extract_text()

        return text
    
    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        text = '\n'.join([p.text for p in doc.paragraphs])

        return text
    
    else:
        raise ValueError("Invalid support format, please upload PDF/DOCS")
