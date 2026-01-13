import pytest
import json
from unittest.mock import Mock, patch
from app import app, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Test que la página principal carga"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Chat con LLM' in response.data

def test_chat_endpoint_no_query(client):
    """Test chat sin query"""
    response = client.post('/api/chat', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

@patch('app.groq_client.chat.completions.create')
@patch('app.get_db_connection')
def test_chat_endpoint_success(mock_db, mock_groq, client):
    """Test chat exitoso"""
    # Mock de Groq
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='Respuesta de prueba'))]
    mock_response.usage = Mock(total_tokens=100)
    mock_groq.return_value = mock_response
    
    # Mock de base de datos
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = [1]
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn
    
    # Petición
    response = client.post('/api/chat', json={
        'query': 'Hola, ¿cómo estás?',
        'session_id': 'test_session'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'response' in data
    assert data['response'] == 'Respuesta de prueba'

def test_history_endpoint_no_session(client):
    """Test historial sin sesión específica"""
    response = client.get('/api/history')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'history' in data

if __name__ == '__main__':
    pytest.main([__file__, '-v'])