---
title: Supply Chain Disruption Triage RL Environment
emoji: 🌍
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# 🌍 Supply Chain Disruption Triage RL Environment

> **Expert-level reinforcement learning environment for real-time supply chain triage.**

**Project Lead:** MAYANK CHOUHAN  
**Corpus:** Supply Chain Disruption Triage

---

## 🎯 Objective
Simulate a real-world procurement system where an AI agent must reallocate purchase orders during supply chain disruptions. The agent must optimize:
- **Stockout avoidance (40%)**
- **Cost efficiency (30%)**
- **Lead time (20%)**
- **Budget adherence (10%)**

This is an **OpenEnv-compliant** multi-objective constraint-satisfaction environment.

---

## 🏗️ Architecture
- **Environment**: Python-based RL environment with Pydantic typed models.
- **Server**: FastAPI exposing the OpenEnv HTTP API.
- **Data**: Seed-based synthetic generator producing suppliers, SKUs, and orders.
- **Tasks**: 3 predefined tasks (Easy, Medium, Hard) plus a Live Realworld Crisis mode.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11
- Docker (optional)

### 2. Local Installation
```bash
git clone https://github.com/MAYANK2264/NovaAI-Hackethon.git
cd NovaAI-Hackethon/supply-chain-env
pip install -r requirements.txt
```

### 3. Run the Server
```bash
python server.py
# Server will be running at http://localhost:8080
```

### 4. Run Baseline Inference
```bash
# Set environment variables for LLM (if using LLM agent)
# export HF_TOKEN=your_token
# export MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct

python inference.py --all-tasks
```

---

## 🔌 API Usage

### `POST /reset`
Initialize/Reset the environment for a specific task.
```json
{
  "task_id": "task_single_supplier_failure"
}
```

### `POST /step`
Submit an action and receive the next observation and reward.
```json
{
  "action": {
    "reallocations": [
      {
        "order_id": "PO-0001",
        "new_supplier_id": "SUP-02",
        "quantity": 100,
        "priority": "urgent"
      }
    ],
    "cancel_orders": [],
    "split_orders": [],
    "reasoning": "Rerouting due to supplier failure."
  }
}
```

### `GET /validate`
Check environment health and task availability.

---

## 🐋 Docker Deployment
```bash
docker build -t supply-chain-env .
docker run -p 8080:8080 supply-chain-env
```

## 🏆 Hackathon Submission Details
- **Project**: Supply Chain Disruption Triage
- **Author**: MAYANK CHOUHAN
- **Compliance**: OpenEnv v1.0
