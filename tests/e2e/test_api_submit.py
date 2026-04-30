from fastapi.testclient import TestClient

from genai_taskq.api.app import app


def test_submit_and_list() -> None:
    client = TestClient(app)
    res = client.post("/tasks", json={"prompt": "ping", "provider": "mock"})
    assert res.status_code == 200
    list_res = client.get("/tasks")
    assert list_res.status_code == 200
    assert any(item["prompt"] == "ping" for item in list_res.json())
