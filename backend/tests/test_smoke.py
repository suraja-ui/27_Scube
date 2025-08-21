from fastapi.testclient import TestClient
from app.main import app

def test_docs_loads():
    c = TestClient(app)
    r = c.get('/openapi.json')
    assert r.status_code == 200
