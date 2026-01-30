import pytest
from unittest.mock import MagicMock, patch
from services.wger_service import WgerService, WgerImage

@patch('services.wger_service.requests.get')
def test_wger_search_images(mock_get):
    # Setup mock
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "suggestions": [
            {
                "value": "Bench Press",
                "data": {
                    "id": 101,
                    "baseId": 55,
                    "name": "Bench Press",
                    "category": "Chest",
                    "image": "media/exercise-images/101.jpg",
                    "image_thumbnail": "media/exercise-images/101-thumb.jpg"
                }
            }
        ]
    }
    mock_get.return_value = mock_response

    # Init service
    service = WgerService()

    # Test search
    results = service.search_images("bench", per_page=10)

    # Verify
    assert len(results) == 1
    item = results[0]
    assert isinstance(item, WgerImage)
    assert item.id == 101
    assert item.name == "Bench Press"
    assert "https://wger.de/media/exercise-images/101.jpg" in item.image
    
    # Verify URL construction
    args, kwargs = mock_get.call_args
    assert "term=bench" in args[0]
    assert "limit=10" in args[0]

@patch('services.wger_service.requests.get')
def test_wger_search_images_empty(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"suggestions": []}
    mock_get.return_value = mock_response

    service = WgerService()
    results = service.search_images("unknown")
    assert results == []

@patch('services.wger_service.requests.get')
def test_wger_search_error(mock_get):
    mock_get.side_effect = Exception("API Error")
    
    service = WgerService()
    results = service.search_images("error")
    assert results == []
