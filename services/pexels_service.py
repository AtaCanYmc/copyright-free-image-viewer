from typing import List, Optional, Tuple, Any
import os
import requests
from dotenv import load_dotenv
from pexels_api import API
from pexels_api.tools import Photo
from core.db import get_db
from core.models import Image, ImageStatus
from utils.common_utils import get_remote_size, create_folders_if_not_exist
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


    def find_download_url(self, photo: Photo) -> Tuple[Optional[str], float]:
        url_list = [photo.original, photo.large2x, photo.large, photo.medium, photo.small]
        url_indx = 0
        content_kb = 0
        
        # Select best size under limit
        while url_indx < len(url_list):
            image_info = get_remote_size(url_list[url_indx])
            content_kb = image_info.get('kb_decimal', 0)
            if content_kb <= self.max_image_kb:
                break
            url_indx += 1
            
        if url_indx >= len(url_list):
            logger.info(f"Skipped image {photo.id} (all sizes exceed {self.max_image_kb} KB)")
            return None, None

        return url_list[url_indx], content_kb


    def download_image(self, photo: Photo, folder_path: str) -> bool:
        url, content_kb = self.find_download_url(photo)
        if not url:
            return False
        
        try:
            image_data = requests.get(url, timeout=30)
        except requests.RequestException as e:
            logger.error(f"Error downloading image {photo.id} from Pexels: {e}")
            return False

        image_path = os.path.join(folder_path, f"{photo.id}.{photo.extension}")
        create_folders_if_not_exist([folder_path])
        
        with open(image_path, 'wb') as file:
            file.write(image_data.content)

        logger.info(f"Downloaded image {photo.id} to {image_path} ({content_kb:.2f} KB)")
        return True


    def add_image_to_db(self, term_str: str, img: Any, api_source: str):
        db = next(get_db())
        term_obj = db.query(SearchTerm).filter(SearchTerm.term == term_str).first()

        if not term_obj:
            logger.error(f"Term {term_str} not found in DB")
            return

        img_id = str(getattr(img, 'id', 'unknown'))
        url_original = getattr(img, "large2x", None) or getattr(img, "original", None)
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

        image_path = os.path.join(folder_path, f"{photo.id}.{photo.extension}")
        create_folders_if_not_exist([folder_path])
        
        with open(image_path, 'wb') as file:
            file.write(image_data.content)

        logger.info(f"Downloaded image {photo.id} to {image_path} ({content_kb:.2f} KB)")
        return True


    def add_image_to_db(self, term_str: str, img: Any, api_source: str):
        db = next(get_db())
        term_obj = db.query(SearchTerm).filter(SearchTerm.term == term_str).first()

        if not term_obj:
            logger.error(f"Term {term_str} not found in DB")
            return

        img_id = str(getattr(img, 'id', 'unknown'))
        url_large = getattr(img, "large2x", None) or getattr(img, "original", None)
        url_thumbnail = getattr(img, "tiny", None)

        new_image = Image(
            source_id=img_id,
            source_api=api_source,
            url_large=url_large,
            url_thumbnail=url_thumbnail,
            status=ImageStatus.APPROVED.value,
            search_term_id=term_obj.id
        )
        db.add(new_image)
        db.commit()
