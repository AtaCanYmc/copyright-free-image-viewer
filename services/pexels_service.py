from typing import List
import os
from dotenv import load_dotenv
from pexels_api import API
from pexels_api.tools import Photo
from core.db import get_db
from core.models import Image, ImageStatus, SearchTerm
from utils.log_utils import logger
from services.image_service import ImageService

load_dotenv()

class PexelsService(ImageService):
    def __init__(self):
        self.api_key = os.getenv('PEXELS_API_KEY')
        if not self.api_key:
            logger.warning("PEXELS_API_KEY is not set.")
        else:
            self.api = API(self.api_key)
            
        self.max_image_kb = int(os.getenv('MAX_KB_IMAGE_SIZE', '512'))


    def search_images(self, term: str, page: int = 1, per_page: int = 15) -> List[Photo]:
        if not self.api_key:
            return []
            
        try:
            self.api.search(term, page=page, results_per_page=per_page)
            return self.api.get_entries()
        except Exception as e:
            logger.error(f"Error fetching images from Pexels for term '{term}': {e}")
            return []


    def get_all_images(self) -> list[Image]:
        db = next(get_db())
        return db.query(Image).filter(Image.source_api == 'pexels').all()


    def add_image_to_db(self, term_str: str, img: Photo, api_source: str):
        db = next(get_db())
        term_obj = db.query(SearchTerm).filter(SearchTerm.term == term_str).first()

        if not term_obj:
            logger.error(f"Term {term_str} not found in DB")
            return

        img_id = str(getattr(img, 'id', 'unknown'))
        url_original = getattr(img, "original", None)
        url_thumbnail = getattr(img, "tiny", None)
        url_page = getattr(img, "url", None)

        new_image = Image(
            source_id=img_id,
            source_api=api_source,
            url_original=url_original,
            url_thumbnail=url_thumbnail,
            url_page=url_page,
            status=ImageStatus.APPROVED.value,
            search_term_id=term_obj.id
        )
        db.add(new_image)
        db.commit()
