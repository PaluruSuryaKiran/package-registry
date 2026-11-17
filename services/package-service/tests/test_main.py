import pytest


def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_package_returns_201_and_body(client):
    response = client.post(
        "/packages", json={"name": "curl", "description": "transfer tool"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "curl"
    assert body["description"] == "transfer tool"
    assert "created_at" in body
    assert "id" not in body


def test_create_package_twice_returns_409(client):
    client.post("/packages", json={"name": "curl"})
    response = client.post("/packages", json={"name": "curl"})
    assert response.status_code == 409


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"name": "Curl"},
        {"name": "1curl"},
        {"name": "c"},
        {"name": "my_tool"},
        {"name": "curl", "id": 5},
        {"name": "curl", "description": "x" * 501},
    ],
)
def test_create_package_invalid_body_returns_422(client, payload):
    response = client.post("/packages", json=payload)
    assert response.status_code == 422