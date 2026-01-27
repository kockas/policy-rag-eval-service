import asyncio
import pytest


@pytest.mark.asyncio
async def test_run_events_emitted(client):
    r = await client.post("/query", json={"question": "Explain FINMA role", "top_k": 3})
    run_id = r.json()["run_id"]

    await asyncio.sleep(1.2)

    r2 = await client.get(f"/runs/{run_id}/events")
    assert r2.status_code == 200

    events = r2.json()
    event_types = [e["type"] for e in events]

    # order can be deterministic in our current design
    assert "run_created" in event_types
    assert "retrieved" in event_types
    assert "run_started" in event_types
    assert "run_succeeded" in event_types
