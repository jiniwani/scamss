from fastapi.testclient import TestClient
from src.app.main import app


client = TestClient(app)


def test_healthz():
    resp = client.get('/healthz')
    assert resp.status_code == 200
    assert resp.json()['status'] == 'ok'


def test_analyze_low_risk_placeholder():
    body = {
        "conversation_id": "uuid",
        "messages": [
            {
                "message_id": "m1",
                "sender": "user",
                "content": "How was your day?",
                "timestamp": "2025-09-30T10:30:00Z"
            }
        ]
    }
    resp = client.post('/api/v1/analyze', json=body)
    assert resp.status_code == 200
    data = resp.json()
    assert 'risk_tier' in data
    assert 'score' in data


