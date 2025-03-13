from src.procurement_ai.state.procurement_state import ProcurementState
from src.procurement_ai.tools.procurement import SourcingManager

def create_sourcing_events(state: ProcurementState) -> ProcurementState:
    return SourcingManager().create_sourcing_event(state)