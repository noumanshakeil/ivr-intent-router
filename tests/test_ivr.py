import pytest

@pytest.mark.asyncio
async def test_route(client):
    await client.post("/api/intents", json={"name": "billing", "description": "invoice payment refund charge"})
    await client.post("/api/rules", json={"intent_name": "billing", "destination": "queue.billing", "min_confidence": 0.2})
    r = await client.post("/api/route", json={"utterance": "I need a refund on my invoice charge"})
    assert r.status_code == 200
    body = r.json()
    assert body["destination"]
    assert "confidence" in body
