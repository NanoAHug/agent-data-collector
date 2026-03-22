# DataCollector

In the near future, data will become the most valuable core asset. To adapt for that era, I suggest everyone start preparing data now. When computing power advances to make personal LLMs a reality, you can quickly fine-tune your own Agent assistant (collecting memories to resurrect your electronic servant in the future... just kidding).

## Project Structure

```
agent-data-collector/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration management
│   ├── dependencies.py      # Shared dependencies
│   ├── api/
│   │   ├── router.py        # API routes aggregation
│   │   └── endpoints/       # API endpoints
│   │       ├── collect.py
│   │       ├── conversations.py
│   │       └── stats.py
│   ├── core/
│   │   └── security.py      # Authentication logic
│   ├── db/
│   │   ├── base.py          # SQLAlchemy Base
│   │   ├── session.py       # Database connection
│   │   └── models.py        # ORM models
│   ├── schemas/
│   │   └── conversation.py  # Pydantic models
│   ├── services/
│   │   └── conversation.py  # Business logic
│   └── web/
│       └── routes.py        # Web UI routes
├── scripts/
│   └── generate_token.py    # Token generator
├── tests/
│   └── test_api/
├── templates/
├── pyproject.toml
├── requirements.txt
└── .env.example
```

## Authentication

This system uses a dual authentication mechanism:

1. **API Authentication**: Clients authenticate via Bearer Token in Authorization header
2. **Web Authentication**: Web interface uses password login with Session Cookie

### Generate API Token

Before running the server, generate an API token:

```bash
python scripts/generate_token.py
```

This will:
- Generate a secure random token
- Set it in your environment variables
- Print instructions for manual setup if needed
- Print the token for you to copy and save

**Important: Restart your terminal after running the script for the environment variable to take effect.**

## Installation

```bash
pip install -r requirements.txt
```

Or using pyproject.toml:

```bash
pip install -e .
```

## Run Server

```bash
# Development mode (auto-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Access URLs

- Web Management Interface: http://your-server-ip:8000/ (login required)
- API Documentation: http://your-server-ip:8000/docs
- Data Collection Endpoint: POST http://your-server-ip:8000/api/collect

## API Reference

### POST /api/collect

Submit conversation data to the server.

**Authentication**

All requests must include the API token in the `Authorization` header:

```
Authorization: Bearer <your_api_key>
```

**Request**

```
POST /api/collect
Content-Type: application/json
Authorization: Bearer <your_api_key>
```

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | Unique identifier for the conversation session |
| `timestamp` | string | Yes | ISO 8601 format timestamp of the conversation |
| `user_input` | string | Yes | User's input message |
| `assistant_response` | string | Yes | Assistant's response message |
| `context_messages` | array | No | Array of context messages (e.g., conversation history) |
| `metadata` | object | No | Additional metadata (e.g., model name, tokens used) |

**Example Request Body**

```json
{
  "session_id": "20260322_143022_abc123",
  "timestamp": "2026-03-22T14:30:22.123456",
  "user_input": "What is the weather today?",
  "assistant_response": "I don't have access to real-time weather data.",
  "context_messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help you?"}
  ],
  "metadata": {
    "model": "gpt-4",
    "tokens_used": 150
  }
}
```

**Response**

Success (200):
```json
{
  "status": "success",
  "id": 1
}
```

Error (403):
```json
{
  "detail": "Invalid API key"
}
```

**Examples**

curl:
```bash
curl -X POST "http://your-server-ip:8000/api/collect" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key" \
  -d '{
    "session_id": "20260322_143022",
    "timestamp": "2026-03-22T14:30:22.123456",
    "user_input": "What is the weather?",
    "assistant_response": "I cannot access real-time weather.",
    "context_messages": [],
    "metadata": {}
  }'
```

Python:
```python
import requests

API_URL = "http://your-server-ip:8000/api/collect"
API_KEY = "your_api_key"

def collect_conversation(user_input, assistant_response, session_id, context_messages=None, metadata=None):
    data = {
        "session_id": session_id,
        "timestamp": "2026-03-22T14:30:22.123456",
        "user_input": user_input,
        "assistant_response": assistant_response,
        "context_messages": context_messages or [],
        "metadata": metadata or {}
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    response = requests.post(API_URL, json=data, headers=headers)
    return response.json()

# Usage
result = collect_conversation(
    session_id="20260322_143022",
    user_input="Hello!",
    assistant_response="Hi! How can I help you?"
)
print(result)  # {"status": "success", "id": 1}
```

---

### Web Management Interface API (Login Required)

The following endpoints require login through the Web interface:

- `GET /api/conversations` - Query conversation list
- `GET /api/conversations/{id}` - View conversation details
- `DELETE /api/conversations/{id}` - Delete conversation
- `GET /api/stats` - Get statistics

## Client Integration

```python
DATA_COLLECTION_ENABLED = True
DATA_COLLECTION_SERVER = "http://your-server-ip:8000/api/collect"
DATA_COLLECTION_API_KEY = "your_api_key"  # Generated by scripts/generate_token.py
```

## Data Storage

Data is stored in the `data/conversations.db` SQLite database.

## Development

### Run Tests

```bash
pytest
```

### Code Style

This project follows standard Python conventions. Make sure to format your code before submitting.
