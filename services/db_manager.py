from typing import Any
from core.db import get_db
from core.models import Image, ImageStatus, SearchTerm
from utils.log_utils import logger

class DBManager:
    """Handles all database operations for images fetched from external APIs."""
    
    @staticmethod
    def get_all_images(api_source: str) -> list[Image]:
        db = next(get_db())
        return db.query(Image).filter(Image.source_api == api_source).all()

    @staticmethod
    def update_image_in_db(img: dict, api_source: str):
        db = next(get_db())
        try:
            img_to_update = db.query(Image).filter(
                Image.source_id == str(img.get('id')),
                Image.source_api == api_source
            ).first()

            if img_to_update:
                img_to_update.url_original = img.get('url_original')
                img_to_update.url_thumbnail = img.get('url') or img.get('url_original')
                img_to_update.url_page = img.get('url') or img.get('url_original')
                db.commit()
        except Exception as e:
            logger.error(f"Error updating image in DB: {e}")
            db.rollback()

    @staticmethod
    def add_image_to_db(term_str: str, img: dict, api_source: str):
        db = next(get_db())
        term_obj = db.query(SearchTerm).filter(SearchTerm.term == term_str).first()

        if not term_obj:
            logger.error(f"Term {term_str} not found in DB")
            return

        img_id = str(img.get('id', 'unknown'))
        url_original = img.get('url_original')
        url_thumbnail = img.get('url') or url_original
        url_page = img.get('url') or url_original
        extension = "jpg"

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
