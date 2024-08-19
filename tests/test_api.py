import unittest
import datetime
from fastapi.testclient import TestClient

from api.main import app


class ApiTest(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_create_and_get_paste(self):
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
                    "text": "print(\"Hello, World!\")",
                    "kind": "python",
                },
            ],
            "expiry": expire_after,
        }
        expire_date = datetime.datetime.now() + datetime.timedelta(seconds=expire_after)

        response = self.client.post("/", json=json_request)
        url = response.json()
        _, key = url.split("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(key), 4)

        response = self.client.get(f"/{key}")
        json_response = response.json()
        api_expire_date = datetime.datetime.strptime(json_response["expiry"], "%Y-%m-%dT%H:%M:%S.%f")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response["files"], json_request["files"])
        self.assertEqual(json_response["key"], key)
        self.assertLess(api_expire_date - expire_date, datetime.timedelta(seconds=10))

    def test_fails_on_empty_text(self):
        json_request = {
            "files": [
                {
                    "name": "",
                    "text": "",
                    "kind": ""
                }
            ],
            "expiry": 3600,
        }
        response = self.client.post("/", json=json_request)
        json_response = response.json()

        self.assertEqual(response.status_code, 422)
        self.assertEqual(json_response["detail"][0]["type"], "string_too_short")
        self.assertIn("text", json_response["detail"][0]["loc"])
        self.assertIn("min_length", json_response["detail"][0]["ctx"].keys())

    def test_fails_on_zero_files(self):
        json_request = {
            "files": [],
            "expiry": 3600,
        }
        response = self.client.post("/", json=json_request)
        json_response = response.json()

        self.assertEqual(response.status_code, 422)
        self.assertEqual(json_response["detail"][0]["type"], "too_short")
        self.assertIn("files", json_response["detail"][0]["loc"])
        self.assertIn("min_length", json_response["detail"][0]["ctx"].keys())

    def test_fails_on_zero_expiry(self):
        json_request = {
            "files": [
                {
                    "name": "hello.py",
                    "text": "print(\"Hello, World!\")",
                    "kind": "python",
                }
            ],
            "expiry": 0,
        }
        response = self.client.post("/", json=json_request)
        json_response = response.json()

        self.assertEqual(response.status_code, 422)
        self.assertEqual(json_response["detail"][0]["type"], "greater_than")
        self.assertIn("expiry", json_response["detail"][0]["loc"])
        self.assertIn("gt", json_response["detail"][0]["ctx"].keys())

    def test_404_on_invalid_paste_key(self):
        response = self.client.get("/abcd")
        self.assertEqual(response.status_code, 404)