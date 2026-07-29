"""Python SDK for constructing and submitting custody assertions."""

from __future__ import annotations

import httpx

from kernel.custody.application.commands import DeclareCustodyAssertion
from kernel.custody.domain.assertions import CommittedCustodyAssertion


class CustodyKernelClient:
    """Small HTTP client for the custody write and read APIs."""

    def __init__(self, base_url: str) -> None:
        """Initialize the client with the API base URL."""

        self._base_url = base_url.rstrip("/")

    def declare_assertion(self, command: DeclareCustodyAssertion) -> CommittedCustodyAssertion:
        """Submit a custody assertion and return the committed event."""

        response = httpx.post(
            f"{self._base_url}/v1/custody/assertions",
            json=command.model_dump(mode="json"),
            timeout=10.0,
        )
        response.raise_for_status()
        return CommittedCustodyAssertion.model_validate(response.json()["assertion"])
