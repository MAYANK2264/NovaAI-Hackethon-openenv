"""
Uniform multi-objective grader for all tasks.
Follows strict OpenEnv spec:
- Stockout avoidance (40%)
- Cost efficiency (30%)
- Lead time (20%)
- Budget constraints (10%)
"""
from __future__ import annotations
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from env.models import Observation, PurchaseOrder, Supplier, Reward, RewardBreakdown


class GradeResult(BaseModel):
    task_id: str
    final_score: float           # 0.0 – 1.0
    passed: bool                 # True if score >= 0.5
    components: Dict[str, float] = Field(default_factory=dict)
    notes: List[str] = Field(default_factory=list)


def grade(task_id: str, obs: Observation) -> GradeResult:
    """
    Uniform multi-objective grader.
    - Stockout avoidance (40%): How many affected orders were rerouted?
    - Cost efficiency (30%): Spend relative to budget.
    - Lead time (20%): Deliveries within requirements.
    - Budget constraints (10%): No budget overruns.
    """
    notes = []
    penalties = 0.0
    
    # Identify disrupted suppliers
    disrupted_sids = set()
    for d in obs.disruptions:
        disrupted_sids.update(d.affected_supplier_ids)
    
    # 1. Stockout Avoidance (40%)
    # Orders are 'at_risk' if their original_supplier is disrupted.
    # They are 'resolved' if they are now allocated to a non-disrupted supplier.
    at_risk_orders = [o for o in obs.pending_orders if o.original_supplier_id in disrupted_sids]
    resolved_orders = [o for o in at_risk_orders if o.status == "allocated" and o.current_supplier_id not in disrupted_sids]
    
    stockout_score = 1.0
    if at_risk_orders:
        stockout_score = len(resolved_orders) / len(at_risk_orders)
    notes.append(f"Stockout avoidance: {stockout_score:.2f} ({len(resolved_orders)}/{len(at_risk_orders)} resolved)")

    # 2. Cost Efficiency (30%)
    # spend <= total_budget
    total_cost = sum(o.unit_cost * o.quantity for o in obs.pending_orders if o.status != "cancelled")
    cost_score = max(0.0, 1.0 - (total_cost / obs.total_budget)) if obs.total_budget > 0 else 1.0
    notes.append(f"Cost efficiency: {cost_score:.2f}")

    # 3. Lead Time (20%)
    supplier_map = {s.supplier_id: s for s in obs.suppliers}
    correct_lt = 0
    fulfilled = [o for o in obs.pending_orders if o.current_supplier_id in supplier_map]
    for o in fulfilled:
        sup = supplier_map[o.current_supplier_id]
        if sup.lead_time_days <= o.required_by_day:
            correct_lt += 1
    
    lt_score = (correct_lt / len(fulfilled)) if fulfilled else 1.0
    notes.append(f"Lead time score: {lt_score:.2f}")

    # 4. Budget Constraints (10%)
    budget_score = 1.0 if obs.budget_remaining >= 0 else 0.0
    notes.append(f"Budget compliance: {budget_score:.2f}")

    # Penalties
    for o in obs.pending_orders:
        if o.current_supplier_id:
            sup = supplier_map.get(o.current_supplier_id)
            if not sup:
                penalties += 0.05 # invalid supplier
            elif sup.is_disrupted:
                penalties += 0.1 # reallocated to disrupted supplier
            elif o.sku not in sup.available_skus:
                penalties += 0.05 # SKU mismatch

    final_score = (
        stockout_score * 0.40 +
        cost_score * 0.30 +
        lt_score * 0.20 +
        budget_score * 0.10
    ) - penalties
    
    final_score = max(0.0, min(1.0, final_score))
    
    return GradeResult(
        task_id=task_id,
        final_score=round(final_score, 4),
        passed=final_score >= 0.5,
        components={
            "stockout_avoidance": stockout_score,
            "cost_efficiency": cost_score,
            "lead_time": lt_score,
            "budget": budget_score,
            "penalties": penalties
        },
        notes=notes
    )



GRADERS = {
    "task_single_supplier_failure": grade,
    "task_port_congestion_cascade": grade,
    "task_multi_shock_crisis": grade,
    "task_live_realworld_crisis": grade,
}
