from abc import ABC
from typing import Any, Optional

from core.models import Image


class ImageService(ABC):
    def __init__(self):
        pass

    def search_images(self, term: str, page: int = 1, per_page: int = 15) -> list[Any]:
        pass

    def get_all_images(self) -> list[Image]:
        pass

    def add_image_to_db(self, term_str: str, img: Any, api_source: str):
        pass

    def update_image_in_db(self, img: Any):
        pass

    def fetch_image(self, id: int) -> Optional[Any]:
        pass

    def json_to_image(self, item: dict[str, Any]) -> Any:
        pass
