import pandas as pd
import os

def convert_to_csv(test_suite, file_name: str) -> None:
    """
    Converts a TestSuite object into a CSV file using pandas.
    
    Each test step becomes one row.
    """
    
    rows = []

    for test_case in test_suite.test_cases:
        preconditions_str = "\n".join(test_case.preconditions or [])
        
        for step in test_case.steps:
            rows.append({
                "TestCaseID": test_case.id,
                "RequirementID": test_case.requirement_id,
                "Title": test_case.title,
                "Preconditions": preconditions_str,
                "StepNumber": step.step_number,
                "Action": step.action,
                "ExpectedResult": step.expected_result,
                "Priority": test_case.priority,
                "agent_instructions":test_case.instructions
            })

    df = pd.DataFrame(rows)
    # Save to CSV
    os.makedirs("Output", exist_ok=True)
    path = "Output/"+file_name
    df.to_csv(path, index=False, encoding="utf-8")