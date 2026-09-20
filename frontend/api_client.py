from typing import Any

import requests


class APIClientError(Exception):
    """Base error for frontend API requests."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(APIClientError):
    """The access token is missing, invalid, or expired."""


class IntelligenceNotFoundError(APIClientError):
    """No Student Intelligence snapshot exists yet."""


class BackendUnavailableError(APIClientError):
    """The backend could not be reached."""


class APIClient:
    """Small authenticated client for the NOVI backend."""

    def __init__(self, base_url: str, access_token: str):
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
        }

    def get_student_intelligence(self) -> dict[str, Any]:
        """Return the latest Student Intelligence snapshot."""
        try:
            response = requests.get(
                f"{self.base_url}/module2/intelligence",
                headers=self.headers,
                timeout=10,
            )
        except requests.RequestException as error:
            raise BackendUnavailableError(
                "NOVI backend is unavailable."
            ) from error

        detail = self._detail(response)

        if response.status_code == 200:
            return response.json()

        if response.status_code == 401:
            raise AuthenticationError(
                detail or "Your authentication has expired.",
                status_code=401,
            )

        if response.status_code == 404:
            raise IntelligenceNotFoundError(
                detail or "Student intelligence not found.",
                status_code=404,
            )

        raise APIClientError(
            detail or f"NOVI API request failed ({response.status_code}).",
            status_code=response.status_code,
        )

    @staticmethod
    def _detail(response: requests.Response) -> str | None:
        try:
            payload = response.json()
        except ValueError:
            return None

        if isinstance(payload, dict):
            detail = payload.get("detail")
            if isinstance(detail, str):
                return detail

        return None
