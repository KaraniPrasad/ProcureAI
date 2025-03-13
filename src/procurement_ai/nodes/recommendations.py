from src.procurement_ai.state.procurement_state import ProcurementState
from src.procurement_ai.tools.procurement import RecommendationEngine

def suggest_aggregation(state: ProcurementState) -> ProcurementState:
    return RecommendationEngine().suggest_aggregation(state)