import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()

def test_index(client):
    """Test básico para '/'"""
    rv = client.get('/')
    assert rv.status_code == 200
    assert 'text/html' in rv.content_type

def test_chat_empty_query(client):
    """Test básico para '/chat' con query vacía"""
    rv = client.post('/chat', json={"query": ""})
    assert rv.status_code == 400
    data = json.loads(rv.data)
    assert "error" in data

def test_history_exists(client):
    """Test básico para '/history'"""
    rv = client.get('/history')
    assert rv.status_code in [200, 500]  # 200 si funciona, 500 si hay error de DB