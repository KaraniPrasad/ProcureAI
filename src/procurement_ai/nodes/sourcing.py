from state.procurement_state import ProcurementState
from tools.procurement import SourcingManager

def create_sourcing_events(state: ProcurementState) -> ProcurementState:
    return SourcingManager().create_sourcing_event(state)