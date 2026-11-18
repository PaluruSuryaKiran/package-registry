import pytest
from package_service.models import Package, Release
from package_service.versions import parse_version

def add_package(session, name, versions=()):
    """Insert a package and its releases directly, bypassing the API."""
    package = Package(name=name)
    for text in versions:
        v = parse_version(text)
        package.releases.append(
            Release(version=text, major=v.major, minor=v.minor, patch=v.patch)
        )
    session.add(package)
    session.commit()
    return package

def test_health(client):
    response = client.get("/health")
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

def test_get_package_returns_200_and_body(client):
    client.post("/packages", json={"name": "curl", "description": "transfer tool"})
    response = client.get("/packages/curl")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "curl"
    assert body["description"] == "transfer tool"
    assert "created_at" in body
    assert "latest_version" in body 


def test_get_package_without_releases_has_null_latest(client, session):
    add_package(session, "curl")
    response = client.get("/packages/curl")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "curl"
    assert body["latest_version"] is None
    assert "id" not in body


def test_get_package_latest_is_numeric_not_text_order(client, session):
    add_package(session, "curl", ["1.2.0", "1.9.0", "1.10.0"])
    response = client.get("/packages/curl")
    assert response.json()["latest_version"] == "1.10.0"


def test_get_package_latest_is_highest_not_newest(client, session):
    add_package(session, "curl", ["2.0.0", "1.5.0"])
    response = client.get("/packages/curl")
    assert response.json()["latest_version"] == "2.0.0"


def test_get_package_ignores_other_packages_releases(client, session):
    add_package(session, "curl", ["8.5.0"])
    add_package(session, "wget", ["1.21.0", "1.24.5"])
    assert client.get("/packages/curl").json()["latest_version"] == "8.5.0"
    assert client.get("/packages/wget").json()["latest_version"] == "1.24.5"


def test_get_package_matches_create_response_shape(client):
    created = client.post("/packages", json={"name": "curl"}).json()
    fetched = client.get("/packages/curl").json()
    assert created == fetched


def test_get_unknown_package_returns_404(client):
    response = client.get("/packages/nope")
    assert response.status_code == 404
    assert "nope" in response.json()["detail"]


def test_get_package_name_is_case_sensitive(client, session):
    add_package(session, "curl")
    assert client.get("/packages/Curl").status_code == 404