"""API endpoints test suite."""

import datetime

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient) -> None:
    """Verify that root endpoint returns welcome message."""
    response = client.get("/")
    assert response.status_code == 200


def test_create_and_get_paste(client: TestClient) -> None:
    """Verify posting a paste correctly saves it and makes it retrievable."""
    expire_after = 3600
    json_request = {
        "files": [
            {
                "name": "hello.txt",
                "text": "hello",
                "kind": "text",
            },
            {
                "name": "hello.py",
                "text": 'print("Hello, World!")',
                "kind": "python",
            },
        ],
        "expiry": expire_after,
    }
    expire_date = datetime.datetime.now() + datetime.timedelta(seconds=expire_after)

    response = client.post("/", json=json_request)
    assert response.status_code == 200
    key = response.json()
    assert len(key) == 4

    response = client.get(f"/{key}")
    assert response.status_code == 200
    json_response = response.json()
    api_expire_date = datetime.datetime.strptime(
        json_response["expiry"], "%Y-%m-%dT%H:%M:%S.%f"
    )

    assert json_response["files"] == json_request["files"]
    assert json_response["key"] == key
    assert api_expire_date - expire_date < datetime.timedelta(seconds=10)


def test_fails_on_empty_text(client: TestClient) -> None:
    """Verify that creating paste with empty text fails with validation error."""
    json_request = {
        "files": [{"name": "", "text": "", "kind": ""}],
        "expiry": 3600,
    }
    response = client.post("/", json=json_request)
    assert response.status_code == 422
    json_response = response.json()
    assert json_response["detail"][0]["type"] == "string_too_short"
    assert "text" in json_response["detail"][0]["loc"]
    assert "min_length" in json_response["detail"][0]["ctx"].keys()


def test_fails_on_zero_files(client: TestClient) -> None:
    """Verify that creating paste with zero files fails with validation error."""
    json_request = {
        "files": [],
        "expiry": 3600,
    }
    response = client.post("/", json=json_request)
    assert response.status_code == 422
    json_response = response.json()
    assert json_response["detail"][0]["type"] == "too_short"
    assert "files" in json_response["detail"][0]["loc"]
    assert "min_length" in json_response["detail"][0]["ctx"].keys()


def test_fails_on_zero_expiry(client: TestClient) -> None:
    """Verify that creating paste with zero expiry fails with validation error."""
    json_request = {
        "files": [
            {
                "name": "hello.py",
                "text": 'print("Hello, World!")',
                "kind": "python",
            }
        ],
        "expiry": 0,
    }
    response = client.post("/", json=json_request)
    assert response.status_code == 422
    json_response = response.json()
    assert json_response["detail"][0]["type"] == "greater_than"
    assert "expiry" in json_response["detail"][0]["loc"]
    assert "gt" in json_response["detail"][0]["ctx"].keys()


def test_404_on_invalid_paste_key(client: TestClient) -> None:
    """Verify that querying a non-existent paste key returns 404."""
    response = client.get("/abcd")
    assert response.status_code == 404
