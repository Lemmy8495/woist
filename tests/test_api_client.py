import unittest
import urllib.error
import warnings

from woistlib.api_client import ApiClient, ApiRequestError


class _FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def read(self) -> bytes:
        return self._payload


class ApiClientTest(unittest.TestCase):
    def test_retries_after_urlerror(self) -> None:
        attempts = {"count": 0}

        def opener(_request, timeout=10):
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise urllib.error.URLError("temporary")
            return _FakeResponse(b'{"ok": true}')

        client = ApiClient(
            user_agent="woist/test",
            max_retries=3,
            opener=opener,
            sleeper=lambda _seconds: None,
        )

        data = client.get_json("https://example.test")
        self.assertEqual(data["ok"], True)
        self.assertEqual(attempts["count"], 2)

    def test_raises_on_non_retry_http_error(self) -> None:
        def opener(_request, timeout=10):
            raise urllib.error.HTTPError(
                url="https://example.test",
                code=400,
                msg="bad request",
                hdrs={},
                fp=None,
            )

        client = ApiClient(user_agent="woist/test", max_retries=3, opener=opener, sleeper=lambda _s: None)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            with self.assertRaises(ApiRequestError):
                client.get_json("https://example.test")


if __name__ == "__main__":
    unittest.main()
