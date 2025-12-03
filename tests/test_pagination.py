import pytest
from app import create_app, db
from app.models import Game
from unittest.mock import patch

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

def test_pagination(client):
    # Mock fetch_collection to return 50 items
    items = [{'@objectid': str(i), 'name': {'@value': f'Game {i}'}} for i in range(1, 51)]
    mock_data = {'items': {'item': items}}
    
    with patch('app.routes.main.fetch_collection', return_value=mock_data) as mock_fetch:
        with patch('app.routes.main.fetch_things', return_value={'items': {'item': []}}): # Mock details fetch
            # Test Page 1
            response = client.post('/collection', data={'username': 'testuser'})
            assert response.status_code == 200
            assert b'Page 1 of 3' in response.data # 50 items / 24 per page = 3 pages
            
            # Test Page 2 via GET
            response = client.get('/collection?username=testuser&page=2')
            assert response.status_code == 200
            assert b'Page 2 of 3' in response.data
            
            # Test Page 3 via GET
            response = client.get('/collection?username=testuser&page=3')
            assert response.status_code == 200
            assert b'Page 3 of 3' in response.data
