from abc import ABC
from typing import Any

class ImageService(ABC):
    def __init__(self):
        pass
    
    def search_images(self, term: str, page: int = 1, per_page: int = 15) -> list[Any]:
        pass

    def find_download_url(self, photo: Any) -> Optional[str, int]:
        pass
    
    def download_image(self, photo: Any, folder_path: str) -> bool:
        pass

    def add_image_to_db(self, term_str: str, img: Any, api_source: str):
        pass
    
    def fetch_image(self, id: int) -> Optional[Any]:
        pass

    def json_to_image(self, item: Dict[str, Any]) -> Any:
        pass