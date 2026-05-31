from langgraph.types import interrupt


def f_review(state):
    decision = interrupt({
        "testcases":state['test_case_path'],
        "message":"please approve or reject the test cases, if rejected please provide feedback..."
    })

    return {
        "approval_status":decision['status'],
        "feedback":decision['feedback']
        }
