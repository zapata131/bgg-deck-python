import pytest
from unittest.mock import patch, MagicMock

def test_index(client):
    """Test that the index page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"La Matatena" in response.data

@patch('app.routes.main.fetch_collection')
@patch('app.routes.main.fetch_things')
def test_collection_success(mock_fetch_things, mock_fetch_collection, client):
    """Test successful collection fetching."""
    # Mock BGG collection response
    mock_fetch_collection.return_value = {
        'items': {
            'item': [
                {'@objectid': '1', 'name': {'@value': 'Game 1'}},
                {'@objectid': '2', 'name': {'@value': 'Game 2'}}
            ]
        }
    }
    
    # Mock BGG things response
    mock_fetch_things.return_value = {
        'items': {
            'item': [
                {
                    '@id': '1',
                    'name': [{'@value': 'Game 1'}],
                    'image': 'http://example.com/1.jpg',
                    'yearpublished': {'@value': '2020'},
                    'minplayers': {'@value': '2'},
                    'maxplayers': {'@value': '4'},
                    'playingtime': {'@value': '60'},
                    'statistics': {'ratings': {'averageweight': {'@value': '2.5'}}},
                    'link': []
                },
                {
                    '@id': '2',
                    'name': [{'@value': 'Game 2'}],
                    'image': 'http://example.com/2.jpg',
                    'yearpublished': {'@value': '2021'},
                    'minplayers': {'@value': '1'},
                    'maxplayers': {'@value': '5'},
                    'playingtime': {'@value': '30'},
                    'statistics': {'ratings': {'averageweight': {'@value': '1.5'}}},
                    'link': []
                }
            ]
        }
    }

    response = client.post('/collection', data={'username': 'testuser'})
    assert response.status_code == 200
    assert b"Game 1" in response.data
    assert b"Game 2" in response.data

@patch('app.routes.main.fetch_collection')
def test_collection_not_found(mock_fetch_collection, client):
    """Test collection not found."""
    mock_fetch_collection.return_value = None
    response = client.post('/collection', data={'username': 'unknown'})
    assert response.status_code == 404
    assert b"No games found" in response.data

@patch('app.routes.main.fetch_collection')
def test_collection_processing(mock_fetch_collection, client):
    """Test BGG processing (202)."""
    mock_fetch_collection.return_value = {'status': 202}
    response = client.post('/collection', data={'username': 'processing'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"BGG is processing" in response.data
