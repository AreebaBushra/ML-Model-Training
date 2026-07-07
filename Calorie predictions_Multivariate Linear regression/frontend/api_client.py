from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests

DEFAULT_API_URL = os.getenv("CALORIE_API_URL", "http://127.0.0.1:8000")


class APIClient:
    def __init__(self, base_url: str = DEFAULT_API_URL, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/predict",
            json=payload,
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text
            raise RuntimeError(detail)
        return response.json()


def get_client() -> APIClient:
    return APIClient()
