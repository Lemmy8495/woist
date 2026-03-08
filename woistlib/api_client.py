import json
import time
import urllib.error
import urllib.request


class ApiRequestError(RuntimeError):
    pass


class ApiClient:
    RETRY_HTTP_CODES = {429, 500, 502, 503, 504}

    def __init__(
        self,
        user_agent: str,
        timeout: float = 10.0,
        max_retries: int = 3,
        base_backoff: float = 0.4,
        opener=None,
        sleeper=None,
    ) -> None:
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self._opener = opener or urllib.request.urlopen
        self._sleeper = sleeper or time.sleep

    def get_json(self, url: str, user_agent: str | None = None) -> dict | list:
        req = urllib.request.Request(url, headers={"User-Agent": user_agent or self.user_agent})
        last_error = "unbekannter Fehler"

        for attempt in range(1, self.max_retries + 1):
            try:
                with self._opener(req, timeout=self.timeout) as response:
                    return json.loads(response.read().decode("utf-8", errors="replace"))
            except urllib.error.HTTPError as exc:
                last_error = f"HTTP-Fehler bei API-Abfrage: {exc.code}"
                if exc.code in self.RETRY_HTTP_CODES and attempt < self.max_retries:
                    self._sleep_backoff(attempt)
                    continue
                raise ApiRequestError(last_error) from exc
            except urllib.error.URLError as exc:
                last_error = f"Netzwerkfehler bei API-Abfrage: {exc.reason}"
                if attempt < self.max_retries:
                    self._sleep_backoff(attempt)
                    continue
                raise ApiRequestError(last_error) from exc
            except json.JSONDecodeError as exc:
                raise ApiRequestError("Ungültige JSON-Antwort erhalten.") from exc

        raise ApiRequestError(last_error)

    def _sleep_backoff(self, attempt: int) -> None:
        delay = self.base_backoff * (2 ** (attempt - 1))
        self._sleeper(delay)

