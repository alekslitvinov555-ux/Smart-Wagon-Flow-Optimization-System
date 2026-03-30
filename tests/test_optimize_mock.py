from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_optimize_returns_computed_response():
    response = client.post("/optimize", json={"from": "A", "to": "B"})

    assert response.status_code == 200
    assert response.json() == {
        "old_time": 140,
        "new_time": 120,
        "old_route": ["A", "C", "B"],
        "new_route": ["A", "D", "B"],
    }


def test_optimize_returns_404_for_unknown_station():
    response = client.post("/optimize", json={"from": "A", "to": "Z"})

    assert response.status_code == 404
    assert response.json() == {"detail": "No route found"}
