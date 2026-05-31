from langgraph.types import Command
from langgraph.checkpoint.memory import InMemorySaver
from typing import  TypedDict
from langgraph.graph import StateGraph
from langgraph.graph import START,END
from Backend.Agents.requirement_analysis_agent import f_extract_requirements
from Backend.Agents.test_plan_agent import f_test_plan
from Backend.Agents.test_case_agent import f_test_cases
from Backend.Agents.traceability_agent import f_traceability
from Backend.Agents.review_agent import f_review

memory = InMemorySaver()


class QAState(TypedDict):
    file_path:str
    raw_design_text:str
    requirement_analysis:object
    test_plan:object
    test_cases:object
    test_case_path:str
    traceability:object
    approval_status:str
    feedback:str

def route_based_review(state):
    if state['approval_status'].lower() == 'approved':
        return  'n_traceability'
    else:
        return 'n_test_cases'


def build_graph():
    graph = StateGraph(QAState)

    ### Add nodes to graph
    graph.add_node('n_requirement_analysis',f_extract_requirements)
    graph.add_node('n_test_plan',f_test_plan)
    graph.add_node('n_test_cases',f_test_cases)
    graph.add_node('n_review',f_review)
    graph.add_node('n_traceability',f_traceability)

    ### Add edges to graph
    graph.add_edge(START,'n_requirement_analysis')
    graph.add_edge('n_requirement_analysis','n_test_plan')
    graph.add_edge('n_requirement_analysis','n_test_cases')
    graph.add_edge('n_test_plan',END)
    graph.add_edge('n_test_cases','n_review')
    graph.add_conditional_edges('n_review',route_based_review)
    graph.add_edge('n_traceability',END)

    return graph.compile(checkpointer=memory)

# agent = build_graph()

# result  = agent.invoke({'file_path':'SauceDemo_Enterprise_Design_v2.pdf'},config=config)

# while "__interrupt__" in result:

#     print("====Waiting for human Approval====\n",result["__interrupt__"][0].value)

#     is_approved = input("please enter yes or no for approval:\n")

#     if is_approved.lower() == 'yes':
#         decission = {'status':'approved','feedback':''}    

#     else:
#         feedback = input("please enter the feedback for test cases:\n")
#         decission = {'status':'rejected','feedback':feedback}

#     result = agent.invoke(Command(resume=decission),config=config)


# print(f"====File Path state====\n{result['file_path']}")
# print(f"====requirement state====\n{result['requirement_analysis']}")
# print(f"====test_plan state====\n{result['test_plan']}")
# print(f"====test_case state====\n{result['test_cases']}")
# print(f"====traceability state====\n{result['traceability']}")