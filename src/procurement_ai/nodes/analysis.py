from state.procurement_state import ProcurementState
from tools.procurement import ProcurementAnalyzer

def analyze_requisitions(state: ProcurementState) -> ProcurementState:
    return ProcurementAnalyzer().analyze_requisitions(state)