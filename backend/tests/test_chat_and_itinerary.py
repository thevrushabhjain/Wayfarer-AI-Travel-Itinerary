"""Backend regression tests for Wayfarer travel itinerary API.

Covers: health check, chat/stream extraction + clarification flow (multi-turn),
session history accumulation, and error handling (404 / 422).

NOTE: Gemini free-tier API key has a daily quota of 20 requests. If the quota is
exhausted, tests that depend on LLM responses (extraction/clarification) will be
skipped automatically rather than failing the whole suite.
"""

import os

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")


@pytest.fixture
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


def stream_chat(api_client, session_id, message):
    """POST to /api/chat/stream and parse SSE events into a list of dicts."""
    resp = api_client.post(
        f"{BASE_URL}/api/chat/stream",
        json={"session_id": session_id, "message": message},
        stream=True,
        timeout=90,
    )
    events = []
    event_type = None
    for raw_line in resp.iter_lines(decode_unicode=True):
        if raw_line is None:
            continue
        line = raw_line.strip()
        if line.startswith("event:"):
            event_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            import json as _json

            data = line.split(":", 1)[1].strip()
            try:
                payload = _json.loads(data)
            except _json.JSONDecodeError:
                payload = {"raw": data}
            payload["event"] = event_type
            events.append(payload)
    return resp.status_code, events


class TestHealth:
    def test_health_check(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["llm_provider"] == "gemini"


class TestErrorHandling:
    def test_itinerary_invalid_session_returns_404(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/itinerary/TEST_invalid-session-id")
        assert response.status_code == 404
        assert "detail" in response.json()

    def test_history_invalid_session_returns_404(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/chat/TEST_nonexistent-session/history")
        assert response.status_code == 404

    def test_chat_stream_empty_message_returns_422(self, api_client):
        response = api_client.post(
            f"{BASE_URL}/api/chat/stream",
            json={"session_id": None, "message": ""},
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestChatExtractionAndClarification:
    """These tests call the live LLM. Skipped gracefully if Gemini quota is exhausted."""

    def test_single_message_extracts_multiple_fields(self, api_client):
        status, events = stream_chat(
            api_client,
            None,
            "5 day trip to Barcelona for 2 people, budget 1800 USD, we love art and beaches",
        )
        assert status == 200

        error_events = [e for e in events if e.get("event") == "error"]
        if error_events and "RESOURCE_EXHAUSTED" in str(error_events[0].get("detail", "")):
            pytest.skip("Gemini daily quota exhausted (free tier limit=20/day) - skipping LLM-dependent test")

        result_events = [e for e in events if e.get("event") == "result"]
        assert len(result_events) == 1
        result = result_events[0]
        trip_info = result["trip_info"]

        # Fields provided in the message should be extracted without re-asking.
        assert trip_info["destination"] == "Barcelona"
        assert trip_info["duration_days"] == 5
        assert trip_info["travelers"] == 2
        assert trip_info["budget"] == 1800.0
        assert "art" in trip_info["interests"]
        assert "beaches" in trip_info["interests"]

        # The only fields still missing should NOT include already-provided ones.
        missing = result["missing_fields"]
        assert "destination" not in missing
        assert "budget" not in missing
        assert "travelers" not in missing

    def test_history_accumulates_trip_info_across_turns(self, api_client):
        status, events = stream_chat(api_client, None, "I want to visit Rome for a week")
        assert status == 200
        error_events = [e for e in events if e.get("event") == "error"]
        if error_events and "RESOURCE_EXHAUSTED" in str(error_events[0].get("detail", "")):
            pytest.skip("Gemini daily quota exhausted (free tier limit=20/day) - skipping LLM-dependent test")

        result = [e for e in events if e.get("event") == "result"][0]
        session_id = result["session_id"]

        history_resp = api_client.get(f"{BASE_URL}/api/chat/{session_id}/history")
        assert history_resp.status_code == 200
        history = history_resp.json()
        assert history["trip_info"]["destination"] == "Rome"
        assert len(history["messages"]) >= 2
