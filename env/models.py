"""
Typed models for the Supply Chain Disruption Triage environment.
Strict Pydantic BaseModels for OpenEnv compliance.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Supplier(BaseModel):
    supplier_id: str
    name: str
    location: str
    capacity_per_day: int
    cost_per_unit: float
    lead_time_days: int
    reliability_score: float
    available_skus: List[str]
    lat: float = 0.0
    lng: float = 0.0
    is_disrupted: bool = False
    disruption_reason: Optional[str] = None


class PurchaseOrder(BaseModel):
    order_id: str
    sku: str
    quantity: int
    required_by_day: int
    original_supplier_id: str
    unit_cost: float
    current_supplier_id: Optional[str] = None
    dest_lat: float = 34.0522
    dest_lng: float = -118.2437
    status: str = "pending"   # pending | allocated | at_risk | cancelled | fulfilled
    priority: str = "normal"  # urgent | normal | deferrable


class DisruptionEvent(BaseModel):
    disruption_id: str
    event_type: str            # supplier_failure | port_delay | price_spike | shortage | bankruptcy
    affected_supplier_ids: List[str]
    affected_skus: List[str]
    severity: str              # low | medium | high | critical
    description: str
    day_occurred: int
    delay_days: int = 0
    price_multiplier: float = 1.0


class InventoryLevel(BaseModel):
    sku: str
    current_stock: int
    safety_stock: int
    reorder_point: int


class Observation(BaseModel):
    step: int
    task_id: str
    task_description: str
    disruptions: List[DisruptionEvent]
    pending_orders: List[PurchaseOrder]
    suppliers: List[Supplier]
    inventory: List[InventoryLevel]
    demand_forecast: Dict[str, List[int]]
    budget_remaining: float
    total_budget: float
    days_elapsed: int
    stockout_risk_skus: List[str]
    done: bool = False
    info: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Action types
# ---------------------------------------------------------------------------

class ReallocationAction(BaseModel):
    order_id: str
    new_supplier_id: str
    quantity: int
    priority: str = "normal"


class SplitOrderAction(BaseModel):
    order_id: str
    splits: List[ReallocationAction]


class Action(BaseModel):
    reallocations: List[ReallocationAction] = Field(default_factory=list)
    cancel_orders: List[str] = Field(default_factory=list)
    split_orders: List[SplitOrderAction] = Field(default_factory=list)
    reasoning: str = ""


# ---------------------------------------------------------------------------
# Reward
# ---------------------------------------------------------------------------

class RewardBreakdown(BaseModel):
    stockout_avoidance: float
    cost_efficiency: float
    lead_time_score: float
    budget_adherence: float


class Reward(BaseModel):
    total: float
    breakdown: RewardBreakdown
    penalties: Dict[str, float] = Field(default_factory=dict)
    explanation: str = ""


# ---------------------------------------------------------------------------
# Step / Reset results
# ---------------------------------------------------------------------------

class StepResult(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict)


class ResetResult(BaseModel):
    observation: Observation
    info: Dict[str, Any] = Field(default_factory=dict)
