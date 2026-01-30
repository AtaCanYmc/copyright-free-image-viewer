import os
from dataclasses import dataclass
from typing import Any, Optional

import requests
from dotenv import load_dotenv

from core.db import get_db
from core.models import Image, ImageStatus, SearchTerm
from services.image_service import ImageService
from utils.log_utils import logger

load_dotenv()

@dataclass
class PixabayImage:
    id: int
    pageURL: str
    type: str
    tags: str
    previewURL: str
    previewWidth: int
    previewHeight: int
    webformatURL: str
    webformatWidth: int
    webformatHeight: int
    largeImageURL: str
    imageWidth: int
    imageHeight: int
    imageSize: int
    views: int
    downloads: int
    likes: int
    comments: int
    user_id: int
    user: str
    userImageURL: str

class PixabayService(ImageService):
    def __init__(self):
        self.api_key = os.getenv('PIXABAY_API_KEY')
        self.api_url = os.getenv('PIXABAY_API_URL')
        self.max_image_kb = int(os.getenv('MAX_KB_IMAGE_SIZE', '512'))

        if not self.api_key or not self.api_url:
            logger.warning("PIXABAY_API_KEY or PIXABAY_API_URL not set.")


    def json_to_image(self, item: dict[str, Any]) -> PixabayImage:
        return PixabayImage(
            id=item['id'],
            pageURL=item['pageURL'],
            type=item['type'],
            tags=item['tags'],
            previewURL=item['previewURL'],
            previewWidth=item['previewWidth'],
            previewHeight=item['previewHeight'],
            webformatURL=item['webformatURL'],
            webformatWidth=item['webformatWidth'],
            webformatHeight=item['webformatHeight'],
            largeImageURL=item['largeImageURL'],
            imageWidth=item['imageWidth'],
            imageHeight=item['imageHeight'],
            imageSize=item['imageSize'],
            views=item['views'],
            downloads=item['downloads'],
            likes=item['likes'],
            comments=item['comments'],
            user_id=item['user_id'],
            user=item['user'],
            userImageURL=item['userImageURL']
        )


    def get_all_images(self) -> list[Image]:
        db = next(get_db())
        return db.query(Image).filter(Image.source_api == 'pixabay').all()


    def search_images(self, term: str, page: int = 1, per_page: int = 15) -> list[PixabayImage]:
        if not self.api_key:
            return []

        params = {
            'key': self.api_key,
            'q': term,
            'page': page,
            'per_page': per_page,
            'image_type': 'photo',
        }

        try:
            response = requests.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error fetching images from Pixabay for term '{term}': {e}")
            return []

        data = response.json()
        if 'error' in data:
            logger.error(f"Pixabay API error: {data['error']}")
            return []

        return [self.json_to_image(item) for item in data.get('hits', [])]


    def fetch_image(self, id: int) -> Optional[PixabayImage]:
        if not self.api_key:
            return None

        params = {
            'key': self.api_key,
            'id': id,
        }

        try:
            response = requests.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error fetching image from Pixabay for id '{id}': {e}")
            return None

        data = response.json()
        if 'error' in data:
            logger.error(f"Pixabay API error: {data['error']}")
            return None

        return self.json_to_image(data.get('hits', [])[0])


    def update_image_in_db(self, img: PixabayImage):
        db = next(get_db())
        try:
            img_to_update = db.query(Image).filter(
                Image.source_id == img.id,
                Image.source_api == 'pixabay'
            ).first()

            if img_to_update:
                img_to_update.url_original = img.largeImageURL
                img_to_update.url_thumbnail = img.previewURL
                img_to_update.url_page = img.pageURL
                db.commit()
        except Exception as e:
            logger.error(f"Error updating image in DB: {e}")
            db.rollback()

    def is_response_expired(self, response: requests.Response) -> bool:
        content_str = response.text.lower()
        return 'invalid' in content_str or 'expired' in content_str


    def add_image_to_db(self, term_str: str, img: PixabayImage, api_source: str):
        db = next(get_db())
        term_obj = db.query(SearchTerm).filter(SearchTerm.term == term_str).first()

        if not term_obj:
            logger.error(f"Term {term_str} not found in DB")
            return

        img_id = str(getattr(img, 'id', 'unknown'))
        url_original = getattr(img, "largeImageURL", None)
        url_thumbnail = getattr(img, "previewURL", None)
        url_page = getattr(img, "pageURL", None)
        extension = getattr(img, "extension", "jpg")

        new_image = Image(
            source_id=img_id,
            source_api=api_source,
            url_original=url_original,
            url_thumbnail=url_thumbnail,
            url_page=url_page,
            status=ImageStatus.APPROVED.value,
            search_term_id=term_obj.id,
            extension=extension
        )
        db.add(new_image)
        db.commit()
