from pydantic import BaseModel, Field
from typing import List, Optional, Literal


# -----------------------------
# 1. INTRODUCTION
# -----------------------------

class Introduction(BaseModel):
    purpose: str = Field(
        description="Explain why this test plan exists and what it aims to achieve."
    )
    project_overview: str = Field(
        description="Provide a high-level overview of the system or project being tested."
    )
    audience: List[str] = Field(
        description="List of stakeholders or roles who will use or review this test plan (e.g., QA team, PM, developers)."
    )


# -----------------------------
# 2. TEST STRATEGY
# -----------------------------

class TestScope(BaseModel):
    in_scope: List[str] = Field(
        description="List of features, modules, or functionalities that will be tested."
    )
    out_of_scope: List[str] = Field(
        description="List of features or areas explicitly excluded from testing."
    )


class TestStrategy(BaseModel):
    objectives: List[str] = Field(
        description="Key goals of testing (e.g., validate functionality, ensure quality, detect defects)."
    )
    assumptions: List[str] = Field(
        description="Assumptions made while planning testing (e.g., environment availability, data readiness)."
    )
    scope: TestScope = Field(
        description="Defines what is included and excluded from testing."
    )
    test_levels: List[Literal["Unit", "Integration", "System", "UAT", "Exploratory"]] = Field(
        description="Types/levels of testing that will be performed."
    )
    test_types: List[str] = Field(
        description="Types of testing such as functional, regression, performance, etc."
    )


# -----------------------------
# 3. EXECUTION STRATEGY
# -----------------------------

class EntryExitCriteria(BaseModel):
    entry_criteria: List[str] = Field(
        description="Conditions that must be met before testing begins."
    )
    exit_criteria: List[str] = Field(
        description="Conditions that must be met before testing is considered complete."
    )


class DefectManagement(BaseModel):
    tool: str = Field(
        description="Tool used for defect tracking (e.g., JIRA, HP ALM)."
    )
    severity_levels: List[str] = Field(
        description="Defined defect severity categories (e.g., Critical, High, Medium, Low)."
    )
    process: str = Field(
        description="Describe how defects are logged, tracked, fixed, and retested."
    )


class ExecutionStrategy(BaseModel):
    entry_exit: EntryExitCriteria = Field(
        description="Defines when testing starts and ends."
    )
    test_cycles: List[str] = Field(
        description="Description of test cycles/phases (e.g., Cycle 1: critical defects, Cycle 2: regression)."
    )
    defect_management: DefectManagement = Field(
        description="Process and tools used for managing defects."
    )


# -----------------------------
# 4. TEST MANAGEMENT
# -----------------------------

class Risk(BaseModel):
    description: str = Field(
        description="Description of the risk that may impact testing."
    )
    impact: Literal["Low", "Medium", "High"] = Field(
        description="Impact level of the risk."
    )
    mitigation: str = Field(
        description="Plan to reduce or handle the risk."
    )


class Resource(BaseModel):
    role: str = Field(
        description="Role name (e.g., Test Lead, QA Engineer, Developer)."
    )
    responsibility: str = Field(
        description="Key responsibilities of this role in the testing process."
    )


class TestManagement(BaseModel):
    tools: List[str] = Field(
        description="Tools used for test management, execution, or reporting."
    )
    risks: List[Risk] = Field(
        description="List of potential risks and mitigation strategies."
    )
    resources: List[Resource] = Field(
        description="List of team roles and their responsibilities."
    )
    communication_plan: Optional[str] = Field(
        description="How communication will happen between teams (meetings, reports, etc.)."
    )


# -----------------------------
# 5. TEST ENVIRONMENT
# -----------------------------

class TestEnvironment(BaseModel):
    hardware: Optional[str] = Field(
        description="Details about hardware or servers used for testing."
    )
    software: List[str] = Field(
        description="Software, browsers, OS, or tools required for testing."
    )
    setup: Optional[str] = Field(
        description="Description of how the test environment is configured."
    )


# -----------------------------
# 6. TEST PLAN (MAIN MODEL)
# -----------------------------

class TestPlan(BaseModel):
    project_name: str = Field(
        description="Name of the project or application under test."
    )
    version: Optional[str] = Field(
        description="Version of the application being tested."
    )
    introduction: Introduction = Field(
        description="Overview and purpose of the test plan."
    )
    strategy: TestStrategy = Field(
        description="Overall testing approach and scope."
    )
    execution: ExecutionStrategy = Field(
        description="How testing will be executed."
    )
    management: TestManagement = Field(
        description="Test management processes, risks, and resources."
    )
    environment: TestEnvironment = Field(
        description="Details about the test environment setup."
    )
    deliverables: List[str] = Field(
        description="List of outputs such as test cases, reports, and metrics."
    )