# AeroRL — Autonomous Drone Path Finder

A production-grade Reinforcement Learning project where a drone learns
to navigate a dynamic grid environment while avoiding obstacles using PPO.

## Tech Stack

### Backend

- Python 3.11
- FastAPI
- Stable Baselines3 (PPO)
- Gymnasium
- MLflow

### Frontend

- Next.js 15
- Tailwind CSS v4
- TypeScript
- Framer Motion

### Infrastructure

- Docker
- Docker Compose
- GitHub Actions

---

# Quickstart

## 1. Clone repository

```bash
git clone <repo-url>
cd AeroRL
```

## 2. Create Conda environment

```bash
cd backend
conda env create -f environment.yml
conda activate aerorl
```

## 3. Configure environment variables

```bash
copy .env.example .env
```

## 4. Start services

```bash
docker compose up --build
```

# Project Goal

Train a PPO-based autonomous drone agent capable of:

- Navigating toward a goal
- Avoiding dynamic obstacles
- Streaming live simulations to a web dashboard
- Tracking metrics and experiments with MLflow
