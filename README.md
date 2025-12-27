# Message Service API

A production-grade REST API for managing chat messages with room-based organization and pagination support.

## Project Overview

The Message Service provides endpoints for creating and retrieving chat messages organized by rooms. It supports pagination for efficient message retrieval and includes proper error handling and logging.

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type annotations
- **SQLite** - Lightweight database for development and demo purposes


## How to Run Locally

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

```bash
venv\Scripts\activate
```


### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI) is available at `http://localhost:8000/docs`

## How to Run with Docker

### Using Docker Compose

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`


## How to Run Tests

```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

## API Endpoints

### POST `/messages`

Create a new message.

### GET `/rooms/{room_id}/messages`

Get paginated messages for a specific room.

