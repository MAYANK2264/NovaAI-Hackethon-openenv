"""
Inference Script — Supply Chain Disruption Triage
===================================================
Baseline HEURISTIC agent for supply chain disruption triage.

Usage:
    python inference.py
    python inference.py --task task_port_congestion_cascade
    python inference.py --all-tasks
"""

from __future__ import annotations
import os
import sys
import json
import time
import argparse
from typing import List, Dict, Optional

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ENV_BASE_URL: str = os.getenv("ENV_BASE_URL", "http://localhost:8080")

ALL_TASKS = [
    "task_single_supplier_failure",
    "task_port_congestion_cascade",
    "task_multi_shock_crisis",
]

# ---------------------------------------------------------------------------
# Environment HTTP client
# ---------------------------------------------------------------------------

class EnvClient:
    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")

    def reset(self, task_id: str) -> dict:
        r = requests.post(f"{self.base}/reset", json={"task_id": task_id}, timeout=30)
        r.raise_for_status()
        return r.json()

    def step(self, action: dict) -> dict:
        r = requests.post(f"{self.base}/step", json={"action": action}, timeout=30)
        r.raise_for_status()
        return r.json()

    def validate(self) -> dict:
        r = requests.get(f"{self.base}/validate", timeout=10)
        r.raise_for_status()
        return r.json()


# ---------------------------------------------------------------------------
# Heuristic Agent logic
# ---------------------------------------------------------------------------

def get_heuristic_action(obs: dict) -> dict:
    """
    Reroute to cheapest valid supplier, avoid disrupted, respect lead time.
    """
    reallocations = []
    
    disrupted_suppliers = {s["supplier_id"] for s in obs.get("suppliers", []) if s.get("is_disrupted")}
    suppliers = [s for s in obs.get("suppliers", []) if not s.get("is_disrupted")]
    
    # Sort suppliers by cost (cheapest first)
    suppliers.sort(key=lambda x: x.get("cost_per_unit", 999999))
    
    at_risk_orders = [o for o in obs.get("pending_orders", []) if o.get("status") in ("at_risk", "pending")]
    
    budget_remaining = obs.get("budget_remaining", 0)
    
    for order in at_risk_orders:
        sku = order.get("sku")
        required_by = order.get("required_by_day", 0)
        
        # Find cheapest supplier that has SKU and meets lead time
        best_sup = None
        for sup in suppliers:
            if sku in sup.get("available_skus", []) and sup.get("lead_time_days", 999) <= required_by:
                # Check if we have budget (simplified)
                cost_diff = (sup.get("cost_per_unit", 0) - order.get("unit_cost", 0)) * order.get("quantity", 0)
                if budget_remaining >= cost_diff:
                    best_sup = sup
                    budget_remaining -= cost_diff
                    break
        
        if best_sup:
            reallocations.append({
                "order_id": order.get("order_id"),
                "new_supplier_id": best_sup.get("supplier_id"),
                "quantity": order.get("quantity"),
                "priority": order.get("priority", "normal")
            })

    return {
        "reallocations": reallocations,
        "cancel_orders": [],
        "split_orders": [],
        "reasoning": "Heuristic: Reroute to cheapest valid supplier meeting lead time."
    }


# ---------------------------------------------------------------------------
# Episode runner
# ---------------------------------------------------------------------------

def run_episode(
    env: EnvClient,
    task_id: str,
) -> float:
    print("[START]")
    print(f"task_id={task_id}")

    reset_result = env.reset(task_id)
    obs = reset_result["observation"]

    history = []
    final_score = 0.0

    while not obs.get("done"):
        step_num = obs.get("step", 0) + 1
        action = get_heuristic_action(obs)

        try:
            step_result = env.step(action)
        except Exception as exc:
            print(f"[ERROR] Step failed: {exc}")
            break

        reward_info = step_result.get("reward", {})
        reward = reward_info.get("total", 0.0)
        obs = step_result["observation"]
        final_score = reward # In this env, final reward is the grade
        
        print("[STEP]")
        print(f"step={step_num}")
        print(f"action={json.dumps(action)}")
        print(f"reward={reward}")

        if obs.get("done"):
            break

    print("[END]")
    print(f"final_score={final_score}")
    return final_score


def main():
    parser = argparse.ArgumentParser(description="Supply Chain Disruption Triage — Inference")
    parser.add_argument("--task", default="task_single_supplier_failure",
                        choices=ALL_TASKS, help="Task to run")
    parser.add_argument("--all-tasks", action="store_true", help="Run all 3 tasks")
    parser.add_argument("--env-url", default=ENV_BASE_URL, help="Environment base URL")
    args = parser.parse_args()

    env = EnvClient(base_url=args.env_url)

    # Health check
    try:
        env.validate()
    except Exception as exc:
        print(f"CRITICAL: Could not reach environment at {args.env_url}: {exc}")
        sys.exit(1)

    tasks = ALL_TASKS if args.all_tasks else [args.task]

    for task_id in tasks:
        run_episode(env, task_id)


if __name__ == "__main__":
    main()
