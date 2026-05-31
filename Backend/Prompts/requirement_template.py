requirement_template = """
You are an QA expert and have good knowledge of how to extract requirements from a design document text, your task is extract the proper requirements into a structured JSON. important this is you to provide only JSON, no need to give any extra text.Generate only 1 requirement for testing
here is design text:
{raw_text}
"""