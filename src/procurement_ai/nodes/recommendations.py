from state.procurement_state import ProcurementState
from tools.procurement import RecommendationEngine

def suggest_aggregation(state: ProcurementState) -> ProcurementState:
    return RecommendationEngine().suggest_aggregation(state)