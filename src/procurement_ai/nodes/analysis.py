from src.procurement_ai.state.procurement_state import ProcurementState
from src.procurement_ai.tools.procurement import ProcurementAnalyzer

def analyze_requisitions(state: ProcurementState) -> ProcurementState:
    return ProcurementAnalyzer().analyze_requisitions(state)