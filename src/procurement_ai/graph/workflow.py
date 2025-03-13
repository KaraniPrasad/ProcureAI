from langgraph.graph import StateGraph, END
from nodes.analysis import analyze_requisitions
from nodes.recommendations import suggest_aggregation
from nodes.sourcing import create_sourcing_events
from state.procurement_state import ProcurementState

def create_procurement_workflow():
    workflow = StateGraph(ProcurementState)
    
    workflow.add_node("analyze", analyze_requisitions)
    workflow.add_node("recommend", suggest_aggregation)
    workflow.add_node("create_events", create_sourcing_events)
    
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "recommend")
    workflow.add_conditional_edges(
        "recommend",
        lambda state: "create_events" if state.get("recommendations") else END,
        {"create_events": "create_events", END: END}
    )
    workflow.add_edge("create_events", END)
    
    return workflow.compile()