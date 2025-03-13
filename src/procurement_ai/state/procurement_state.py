from typing import TypedDict, List, Dict, Annotated

class ProcurementConfig(TypedDict):
    moq: int
    consolidation_window_days: int

class ProcurementState(TypedDict):
    requisitions: List[Dict]
    config: ProcurementConfig
    clusters: Annotated[List[Dict], "clusters"]
    recommendations: Annotated[List[Dict], "recommendations"]
    sourcing_events: Annotated[List[Dict], "sourcing_events"]
    errors: Annotated[List[str], "errors"]