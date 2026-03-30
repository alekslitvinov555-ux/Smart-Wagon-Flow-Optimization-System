from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_optimize_returns_mock_response():
    response = client.post("/optimize", json={"from": "A", "to": "B"})

    assert response.status_code == 200
    assert response.json() == {
        "old_time": 120,
        "new_time": 95,
        "old_route": ["A", "C", "B"],
        "new_route": ["A", "D", "B"],
    }

