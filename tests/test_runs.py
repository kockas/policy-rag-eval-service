import asyncio
import pytest


@pytest.mark.asyncio
async def test_query_creates_run_and_eventually_succeeds(client):
    # create run
    r = await client.post("/query", json={"question": "What is FINMA?", "top_k": 5})
    assert r.status_code == 200
    payload = r.json()
    assert payload["answer"] == "Queued"
    assert "citations" in payload
    run_id = payload["run_id"]
    assert run_id

    # immediately after creation, state should exist
    r2 = await client.get(f"/runs/{run_id}")
    assert r2.status_code == 200
    state1 = r2.json()["state"]
    assert state1 in ("pending", "running")  # depending on timing

    # wait a bit for async runner to finish
    await asyncio.sleep(1.2)

    r3 = await client.get(f"/runs/{run_id}")
    assert r3.status_code == 200
    assert r3.json()["state"] == "succeeded"
    assert r3.json()["finished_at"] is not None
