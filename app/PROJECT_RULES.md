
## 🎯 Purpose
This project is a **interview exercise**.  
Goal: build a **production-grade backend application** in ~1.5 hours.  
Development is done step-by-step using **Cursor IDE with short, scoped prompts**.

---

## 📦 General Guidelines
- Project hosted on **GitHub**
- Include `.gitignore`
- Include a clear `README.md`
- Prefer **clarity over over-engineering**
- Scope is intentionally limited

---
## 🛠️ Technologies Used

- **Language**: Python 3.11
- **Web Framework**: FastAPI
- **Data Validation**: Pydantic
- **ORM**: SQLAlchemy
- **Database**: SQLite (for interview/demo purposes)
- **Testing**: pytest
- **Containerization**: Docker, docker-compose
- **Logging**: Structured JSON logging
- **AI Assistance**: Cursor IDE (used as a coding assistant)
---

## 🧱 Architecture & Structure
- Clean project structure (example):
```text
app/
├── api/        # Routers (HTTP layer)
├── services/   # Business logic
├── dal/        # Database access layer
├── models/     # ORM models
├── schemas/    # Pydantic schemas
├── core/       # Logging, config, shared utilities
tests/
```

- Clear separation of concerns:
- **Router** – HTTP, validation, request/response
- **Service** – business logic
- **DAL** – database access
- No business logic in routers

---

## 🧠 Code Quality
- Prefer **async code**
- Use **typed Python** everywhere
- Use **OOP** where it adds clarity (classes)
- `/health` endpoint
- Use **docstrings**:
    - Short and clear
    - For every class and public function

---

## 📐 Data & Performance
- Use efficient data structures:
- `dict` / `set` for O(1)
- `deque` for queues
- `defaultdict(list)` to avoid key checks
- Use **generators** where applicable to save memory
- Use `Enum` instead of hard-coded strings
- Use `dataclasses` when many fields are involved
- `frozen=True` when immutability is desired

---

## 🧪 Validation & Schemas
- Use **Pydantic schemas** for all API inputs/outputs
- Schemas define the **API contract**
- Validation happens **before business logic runs**
- ORM models must not be exposed directly

---

## 🧪 Testing
- Use **pytest**
- Write:
  - API tests for endpoint behavior (FastAPI TestClient)
  - Unit tests for **service layer** (business logic, mocked DAL)
  - Unit tests for **DAL** (queries, ordering, pagination)
- Cover:
  - Happy paths
  - Negative / edge cases
- Tests should validate **behavior**, not implementation

---

## 🪵 Logging & Errors
- Use **structured logging (JSON)**
- No `print`
- Proper error handling
- Do not leak internal errors to clients

---

## 🐳 Docker
- Docker support is required
- Dockerfile should reflect production mindset
- venv still be used for local development

---

## 🤖 AI Usage (Cursor)
- Cursor AI is used as an **assistant**, not decision-maker
- Prompts must be:
- Short
- Scoped
- Step-based
- AI should not modify unrelated code unless explicitly asked

---

## 🚫 Out of Scope (Do NOT implement)
- Authentication / Authorization (e.g. JWT)
- Rate limiting
- DB migrations (Alembic instead of `create_all`)
- Idempotency handling
- CORS configuration
- Log level via env vars

---

## 🧭 Interview Context
This project is designed to:
- Demonstrate architectural thinking
- Show production mindset
- Be completed in ~90 minutes
- Be explained clearly during an interview