import pytest
from unittest.mock import patch, MagicMock
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.routes.main.fetch_collection')
@patch('app.routes.main.fetch_things')
@patch('app.services.pdf.generate_pdf')
def test_download_all(mock_generate_pdf, mock_fetch_things, mock_fetch_collection, client):
    # Setup mocks
    mock_fetch_collection.return_value = {
        'items': {
            'item': [
                {'@objectid': '1'},
                {'@objectid': '2'},
                {'@objectid': '3'}
            ]
        }
    }
    mock_fetch_things.return_value = {'items': {'item': []}}
    mock_generate_pdf.return_value = b'%PDF-1.4...'

    # Test download_all=true
    response = client.post('/pdf', data={
        'username': 'testuser',
        'download_all': 'true'
    })

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/pdf'
    
    # Verify fetch_collection was called
    mock_fetch_collection.assert_called_with('testuser')
    
    # Verify fetch_things was called with all IDs
    mock_fetch_things.assert_called_with(['1', '2', '3'])

@patch('app.routes.main.fetch_collection')
@patch('app.routes.main.fetch_things')
@patch('app.services.pdf.generate_pdf')
def test_download_selected(mock_generate_pdf, mock_fetch_things, mock_fetch_collection, client):
    # Setup mocks
    mock_fetch_things.return_value = {'items': {'item': []}}
    mock_generate_pdf.return_value = b'%PDF-1.4...'

    # Test download_all=false with selected_ids
    response = client.post('/pdf', data={
        'username': 'testuser',
        'download_all': 'false',
        'selected_ids': '["10", "20"]'
    })

    assert response.status_code == 200
    
    # Verify fetch_collection was NOT called (optimization)
    mock_fetch_collection.assert_not_called()
    
    # Verify fetch_things was called with selected IDs
    mock_fetch_things.assert_called_with(['10', '20'])
