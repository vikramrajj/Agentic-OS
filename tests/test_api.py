import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"
    assert data["retriever_docs"] >= 10


def test_list_tools_endpoint():
    response = client.get("/api/tools")
    assert response.status_code == 200
    data = response.json()
    assert "available_tools" in data
    tool_names = [t["name"] for t in data["available_tools"]]
    assert "get_system_overview" in tool_names
    assert "check_service_status" in tool_names


def test_run_tool_endpoint_valid():
    response = client.post("/api/tools/run", json={"tool_name": "get_system_overview", "args": {}})
    assert response.status_code == 200
    data = response.json()
    assert data["tool_name"] == "get_system_overview"
    assert data["success"] is True


def test_run_tool_endpoint_invalid():
    response = client.post("/api/tools/run", json={"tool_name": "non_existent_tool", "args": {}})
    assert response.status_code == 404


def test_chat_sync_endpoint():
    response = client.post("/api/chat", json={"message": "Why is my service failing with status=203/EXEC?"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0
    assert "status=203/EXEC" in data["response"] or "ExecStart" in data["response"]
