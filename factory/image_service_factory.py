from services.pexels_service import PexelsService
from services.pixabay_service import PixabayService
from services.unsplash_service import UnsplashService
from services.flickr_service import FlickrService
from services.image_service import ImageService

class ImageServiceFactory:
    """Factory class to manage and provide image services."""
    
    # Pre-instantiate services in a registry dictionary
    _services = {
        'pexels': PexelsService(),
        'pixabay': PixabayService(),
        'unsplash': UnsplashService(),
        'flickr': FlickrService()
    }

    @classmethod
    def get_service(cls, api_type: str) -> ImageService:
        """
        Returns the appropriate service based on api_type.
        Raises ValueError if the service is not found.
        """
        service = cls._services.get(api_type.lower())
        if not service:
            raise ValueError(f"Unknown API type: {api_type}. Available: {list(cls._services.keys())}")
        return service