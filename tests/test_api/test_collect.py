import os

os.environ["DATA_COLLECTION_API_KEY"] = "test_api_key"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_collect_without_auth():
    response = client.post("/api/collect", json={
        "session_id": "test_session",
        "timestamp": "2026-03-22T14:30:22",
        "user_input": "Hello",
        "assistant_response": "Hi there!"
    })
    assert response.status_code == 403


def test_collect_with_invalid_auth():
    response = client.post(
        "/api/collect",
        json={
            "session_id": "test_session",
            "timestamp": "2026-03-22T14:30:22",
            "user_input": "Hello",
            "assistant_response": "Hi there!"
        },
        headers={"Authorization": "Bearer wrong_key"}
    )
    assert response.status_code == 403


def test_collect_with_valid_auth():
    response = client.post(
        "/api/collect",
        json={
            "session_id": "test_session",
            "timestamp": "2026-03-22T14:30:22",
            "user_input": "Hello",
            "assistant_response": "Hi there!"
        },
        headers={"Authorization": "Bearer test_api_key"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_collect_with_context_and_metadata():
    response = client.post(
        "/api/collect",
        json={
            "session_id": "test_session_2",
            "timestamp": "2026-03-22T15:00:00",
            "user_input": "What is the weather?",
            "assistant_response": "I don't know.",
            "context_messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi!"}
            ],
            "metadata": {
                "model": "gpt-4",
                "tokens": 50
            }
        },
        headers={"Authorization": "Bearer test_api_key"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "id" in data
