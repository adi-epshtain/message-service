# Cursor Project Rules

## Language & Stack
- Python 3.11+
- FastAPI
- SQLAlchemy
- Pydantic
- pytest

## Coding Style
- Prefer async code
- Use type hints everywhere
- Short, readable functions
- Try not using globals
- No business logic in routers

## Architecture
- Routers: HTTP layer only
- Services: business logic
- DAL: database access
- Clear separation of concerns

## Testing
- API tests for endpoint behavior
- Unit tests for service logic
- Do not mix API and unit tests
- Prefer minimal, high-signal tests

## Logging & Errors
- Structured JSON logging
- No print statements

## AI Usage
- Use Cursor as an assistant, not a decision maker
- Generate minimal, focused code
- Do not modify unrelated files unless explicitly asked