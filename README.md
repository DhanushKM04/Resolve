# Resolve — AI-Powered Payment Event Investigation Engine

Resolve is an AI-powered payment event investigation engine that reconstructs payment state from event history, detects inconsistencies, and uses AI to explain the root cause.

Instead of only showing the current payment status, Resolve answers:

> **What happened, what is inconsistent, and why?**

---

## 🚀 Problem

Modern payment systems generate large numbers of asynchronous events such as:

- `payment.authorized`
- `payment.captured`
- `payment.failed`
- `order.paid`

These events can arrive out of order, be duplicated, or create inconsistent states across payment and order systems.

Traditional dashboards often show only the final state. They do not explain **why that state exists** or identify conflicting event histories.

Resolve is designed to investigate these inconsistencies automatically.

---

## 💡 Solution

Resolve uses a deterministic-first investigation pipeline:

```text
Payment Events
      ↓
FastAPI API
      ↓
State Reconstruction
      ↓
Conflict Detection
      ↓
Investigation Layer
      ↓
Gemini AI

The deterministic engine first reconstructs the payment state and detects conflicts.

AI investigation is an optional second layer that analyzes the detected conflict and event evidence to provide a concise explanation and advisory recommendation.

✨ Key Features
Payment State Reconstruction

Reconstructs the current payment state from the complete event history rather than relying on a single status field.

Conflict Detection

Detects inconsistent payment states such as:

Invalid state transitions
Order marked as paid without a payment capture
Duplicate events
Out-of-order event delivery
Event Timeline

Displays the sequence of payment events used to reconstruct the payment state.

AI-Assisted Investigation

Gemini analyzes detected conflicts and supplied event evidence to provide:

Summary
Root cause
Evidence
Recommendation

AI investigation is optional and does not block deterministic conflict detection.

Safety-First AI Design

The AI investigator is strictly advisory.

It is explicitly instructed not to execute or recommend direct financial mutations, including:

Capturing payments
Refunding payments
Voiding payments
Retrying payments
Modifying payment state

Recommendations are limited to investigation and verification activities such as reviewing logs, reconciling event history, and verifying payment status.

🧠 Example Investigation
Input Event History
payment.authorized
        ↓
order.paid
Resolve Detection
Current State: PAID

Conflict:
ORDER_PAID_WITHOUT_CAPTURE

Severity:
HIGH

Resolve identifies that the order is marked as paid even though no payment capture event exists.

Gemini can then provide a human-readable investigation of the inconsistency.

📊 Evaluation

Resolve was evaluated using both targeted scenarios and a larger benchmark.

Core Evaluation
Total Tests:     5
Passed Tests:    5
Accuracy:        100%
Large-Scale Benchmark
Benchmark Tests: 100

True Positives:   40
True Negatives:   60
False Positives:   0
False Negatives:   0

Accuracy:         100%
Precision:        100%
Recall:           100%
F1 Score:         100%

The benchmark includes normal payments, failed payments, invalid state transitions, inconsistent order/payment states, and out-of-order event delivery.

🏗️ Architecture
                    ┌─────────────────────┐
                    │   Payment Events    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │       Backend       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   State Engine      │
                    │ State Reconstruction│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Conflict Detector   │
                    └──────────┬──────────┘
                               │
                         Conflict Found?
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Investigator      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Gemini AI         │
                    │ Advisory Analysis   │
                    └─────────────────────┘
🛠️ Technology Stack
Backend
Python
FastAPI
Pydantic
SQLite
Uvicorn
AI
Google Gemini
google-genai
Frontend
React
Vite
JavaScript
CSS
Infrastructure
AWS EC2
Docker
Docker Compose
Nginx
Ubuntu Linux
Development
Git
GitHub
Python
REST APIs
☁️ AWS Deployment

Resolve is deployed on an AWS EC2 instance.

Internet
   │
   ▼
Nginx :80
   │
   ├── React Frontend
   │
   └── /api
        │
        ▼
     FastAPI
        │
        ▼
      Docker
        │
        ▼
      SQLite

The backend container is bound internally to the server and is not directly exposed to the public internet.

🌐 Live Demo

Live application:

http://16.192.216.64

Example Payment
pay_9acc18f0

This example demonstrates:

Current State:
PAID

Conflict:
ORDER_PAID_WITHOUT_CAPTURE

Severity:
HIGH

The live application also supports optional Gemini AI investigation.

🔐 Security

Sensitive credentials are kept outside the source code.

The Gemini API key is stored using environment variables and is not included in the repository.

The frontend never receives the Gemini API key.

Only synthetic payment event data is used for demonstration and evaluation.

📁 Project Structure
Resolve/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── investigator.py
│   │   ├── state_engine.py
│   │   ├── conflict_detector.py
│   │   ├── database.py
│   │   └── models.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   └── ...
│
├── simulator/
│   ├── runner.py
│   └── generator.py
│
├── .gitignore
└── README.md
▶️ Running Locally
Backend
cd backend

python -m venv venv

Activate the environment and install dependencies:

pip install -r requirements.txt

Configure the Gemini API key in .env:

GEMINI_API_KEY=your_api_key

Start the backend:

uvicorn app.main:app --reload

The API will be available at:

http://127.0.0.1:8000
Frontend
cd frontend
npm install
npm run dev

The frontend will be available through the Vite development server.

🧪 Running the Simulator
cd simulator
python runner.py

The simulator generates multiple payment scenarios and evaluates the conflict detector.

It includes:

Normal payment
Failed payment
Invalid capture → failure
Order paid without capture
Out-of-order delivery
🎯 Design Philosophy

Resolve follows a deterministic-first, AI-assisted architecture.

The core payment state and conflict detection are handled by explicit rules rather than an LLM.

AI is used where it provides the most value:

Explaining detected inconsistencies rather than deciding payment state.

This makes the system more predictable, testable, and safer for payment-related investigation workflows.

🔮 Future Improvements

Potential future improvements include:

Streaming AI investigation responses
Event ingestion through message queues
Distributed event storage
Additional payment consistency rules
Authentication and role-based access
Observability and distributed tracing
Automated incident notifications
Multi-provider payment event normalization
👨‍💻 Project

Resolve

AI-powered payment event investigation for identifying, explaining, and investigating inconsistencies in payment event histories.