from unittest.mock import MagicMock, patch

from services.pexels_service import PexelsService


@patch('services.pexels_service.API')
def test_pexels_search(mock_api_cls):
    # Setup mock
    mock_api = MagicMock()
    mock_api_cls.return_value = mock_api

    # Mock search results
    mock_photo = MagicMock()
    mock_photo.id = 123
    mock_api.get_entries.return_value = [mock_photo]

    # Init service
    service = PexelsService()

    # Test search
    results = service.search_images("test", page=1, per_page=10)

    # Verify
    mock_api.search.assert_called_with("test", page=1, results_per_page=10)
    assert len(results) == 1
    assert results[0].id == 123
