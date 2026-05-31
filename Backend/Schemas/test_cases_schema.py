from pydantic import BaseModel,Field
from typing import List

class TestStep(BaseModel):
    step_number: int
    action: str
    expected_result: str

class TestCase(BaseModel):
    id: str
    requirement_id: str
    title: str
    preconditions: List[str]
    steps: List[TestStep]
    priority: str
    instructions:str = Field(description = "This is very important as after we use this to send it to an MCP server")

class TestSuite(BaseModel):
    test_cases: List[TestCase]