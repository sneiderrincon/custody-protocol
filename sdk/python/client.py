"""Python SDK for constructing and submitting custody assertions."""

from __future__ import annotations

import httpx

from kernel.custody.application.commands import DeclareCustodyAssertion
from kernel.custody.domain.assertions import CommittedCustodyAssertion


class CustodyKernelClient:
    """Small HTTP client for the custody write and read APIs."""

    def __init__(self, base_url: str, *, token: str | None = None) -> None:
        """Initialize the client with the API base URL and an optional bearer token.

        ``token`` is optional for backward compatibility with existing call
        sites; the write endpoint now requires a valid JWT bearer token
        (see docs/decisions/0010-jwt-authentication.md), so declare_assertion
        calls made without one will receive a 401 from the API.
        """

        self._base_url = base_url.rstrip("/")
        self._token = token

    def declare_assertion(self, command: DeclareCustodyAssertion) -> CommittedCustodyAssertion:
        """Submit a custody assertion and return the committed event."""

        headers = {"Authorization": f"Bearer {self._token}"} if self._token else None
        response = httpx.post(
            f"{self._base_url}/v1/custody/assertions",
            json=command.model_dump(mode="json"),
            timeout=10.0,
            headers=headers,
        )
        response.raise_for_status()
        return CommittedCustodyAssertion.model_validate(response.json()["assertion"])
