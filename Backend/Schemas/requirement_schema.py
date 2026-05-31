from pydantic import BaseModel, Field
from typing import List, Literal

class Requirement(BaseModel):
    id: str = Field(description="Unique id like Req001 of the requirement")
    title: str = Field(description="title of the requirement")
    description: str
    acceptance_criteria: List[str] = Field(description="what are the acceptance criteria that this requirement should satisfy.")
    priority: Literal["High","Medium","Low"]

class RequirementAnalysis(BaseModel):
    project_name: str
    overview: str
    assumptions: List[str]
    requirements: List[Requirement]