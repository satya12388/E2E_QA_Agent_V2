from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class TraceabilityEntry(BaseModel):
    requirement_id: str = Field(
        description="Unique identifier of the requirement."
    )
    requirement_title: str = Field(
        description="Short title or description of the requirement."
    )
    test_case_ids: List[str] = Field(
        description="List of test case IDs mapped to this requirement."
    )
    coverage_status: str = Field(
        description="Coverage status: Covered, Partial, or Not Covered."
    )


# -----------------------------
# Metrics Section
# -----------------------------

class RTMMetrics(BaseModel):
    total_requirements: int = Field(
        description="Total number of requirements."
    )
    total_test_cases: int = Field(
        description="Total number of unique test cases across all requirements."
    )
    coverage_summary: Dict[str, int] = Field(
        description="Count of requirements by coverage status (Covered, Partial, Not Covered)."
    )
    test_cases_per_requirement: Dict[str, int] = Field(
        description="Number of test cases mapped to each requirement (requirement_id -> count)."
    )
    test_cases_by_priority: Optional[Dict[str, int]] = Field(
        description="Distribution of test cases by priority (High, Medium, Low)."
    )


# -----------------------------
# Main RTM Model
# -----------------------------

class TraceabilityMatrix(BaseModel):
    entries: List[TraceabilityEntry] = Field(
        description="List mapping requirements to test cases."
    )
    metrics: Optional[RTMMetrics] = Field(
        description="Aggregated metrics derived from traceability data."
    )
    summary: Optional[str] = Field(
        description="High-level summary of coverage and key observations."
    )