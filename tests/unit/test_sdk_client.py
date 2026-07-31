from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import httpx

from kernel.custody.application.commands import DeclareCustodyAssertion
from kernel.custody.domain.assertions import CommittedCustodyAssertion
from kernel.custody.domain.events import CustodyEventType
from kernel.custody.domain.value_objects import Provenance
from sdk.python import CustodyKernelClient


def test_sdk_posts_command_and_returns_committed_assertion(monkeypatch) -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    command = DeclareCustodyAssertion(
        claim_id=uuid4(),
        unit_id="sdk-unit",
        event_type=CustodyEventType.MANUFACTURED,
        occurred_at=now,
        provenance=Provenance(
            actor_id=uuid4(),
            adapter_id="sdk-test-adapter",
            declared_at=now,
        ),
    )
    committed = CommittedCustodyAssertion(
        **command.model_dump(),
        global_position=1,
        stream_version=1,
    )

    def fake_post(
        url: str,
        *,
        json: dict[str, object],
        timeout: float,
        headers: dict[str, str] | None,
    ) -> httpx.Response:
        assert url == "http://kernel.test/v1/custody/assertions"
        assert json["unit_id"] == "sdk-unit"
        assert timeout == 10.0
        assert headers is None
        request = httpx.Request("POST", url)
        return httpx.Response(
            201, json={"assertion": committed.model_dump(mode="json")}, request=request
        )

    monkeypatch.setattr(httpx, "post", fake_post)

    client = CustodyKernelClient("http://kernel.test/")

    assert client.declare_assertion(command) == committed


def test_sdk_sends_bearer_token_when_provided(monkeypatch) -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    command = DeclareCustodyAssertion(
        claim_id=uuid4(),
        unit_id="sdk-unit",
        event_type=CustodyEventType.MANUFACTURED,
        occurred_at=now,
        provenance=Provenance(
            actor_id=uuid4(),
            adapter_id="sdk-test-adapter",
            declared_at=now,
        ),
    )
    committed = CommittedCustodyAssertion(
        **command.model_dump(),
        global_position=1,
        stream_version=1,
    )

    def fake_post(
        url: str,
        *,
        json: dict[str, object],
        timeout: float,
        headers: dict[str, str] | None,
    ) -> httpx.Response:
        assert headers == {"Authorization": "Bearer test-token"}
        request = httpx.Request("POST", url)
        return httpx.Response(
            201, json={"assertion": committed.model_dump(mode="json")}, request=request
        )

    monkeypatch.setattr(httpx, "post", fake_post)

    client = CustodyKernelClient("http://kernel.test/", token="test-token")  # noqa: S106

    assert client.declare_assertion(command) == committed

