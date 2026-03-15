# Architecture Decision Record: Technology Stack

## Context and Problem Statement
We need to select a scalable, high-performance, and modern technology stack to build the SkyMind AI Airline Operations Intelligence system. The system requires real-time data streaming, complex machine learning inference, and an interactive 3D and 2D dashboard.

## Considered Options
* Backend: Django, Flask, FastAPI, Node.js
* Frontend: Vanilla React, Next.js, React+Vite
* Machine Learning: TensorFlow, PyTorch, Scikit-learn
* Real-time Messaging: WebSockets, Server-Sent Events

## Decision Outcome
* **Backend:** FastAPI (Python) - Exceptionally fast, async support, and native integration with the Python ML ecosystem.
* **Frontend:** React + Vite - Fast development build times, excellent ecosystem for Mapbox/Deck.gl.
* **Machine Learning:** Scikit-learn (XGBoost) for tabular baselines, PyTorch for Temporal Graph Neural Networks (TGNs) and MARL.
* **Real-time Messaging:** WebSockets for bidirectional low-latency updates (essential for the live flight map).

## Consequences
* Seamless integration of ML models into the backend (since both are Python).
* High performance handling multiple concurrent requests due to FastAPI's async nature.
* We must strictly enforce typing in Python to prevent runtime errors (using Pydantic).
