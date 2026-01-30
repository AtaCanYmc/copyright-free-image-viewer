import os
import requests
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

from core.db import get_db
from core.models import Image, ImageStatus, SearchTerm
from services.image_service import ImageService
from utils.log_utils import logger

load_dotenv()

@dataclass
class WgerImage:
    id: int
    base_id: int
    value: str
    name: str
    category: str
    image: str
    image_thumbnail: str

class WgerService(ImageService):
    def __init__(self):
        self.wger_api_url = os.getenv("WGER_API_URL", "https://wger.de/api/v2")
        self.wger_base_url = os.getenv('WGER_BASE_URL', "https://wger.de")

    def _generate_search_url(self, term: str, limit=15, lang='en') -> str:
        return f"{self.wger_api_url}/exercise/search/?language={lang}&term={term}&limit={limit}"

    def json_to_image(self, json_data: dict) -> WgerImage:
        return WgerImage(
            value=json_data['value'],
            id=json_data['data']['id'],
            base_id=json_data['data']['baseId'],
            name=json_data['data']['name'],
            category=json_data['data']['category'],
            image=f"{self.wger_base_url}/{json_data['data']['image']}",
            image_thumbnail=f"{self.wger_base_url}/{json_data['data']['image_thumbnail']}",
        )

    def search_images(self, term: str, page: int = 1, per_page: int = 15) -> List[WgerImage]:
        """
        Search for images in Wger API.
        Note: Wger search endpoint pagination might work differently or not be supported in the same way.
        This implementation uses the existing search logic from wger_utils.
        """
        # Wger search seems to use 'limit' but maybe not 'page' in the same way as standard paginated APIs in this specific endpoint?
        # The original utils used 'limit'. We will map per_page to limit.
        url = self._generate_search_url(term, limit=per_page)
        exercises = []

        try:
            response = requests.get(url).json()
            if 'suggestions' in response:
                data = response['suggestions']
                for img in data:
                    w_img = self._convert_json_to_wger_image(img)
                    exercises.append(w_img)
            return exercises
        except Exception as e:
            logger.error(f"Error fetching images from Wger for term '{term}': {e}")
            return []

    def get_all_images(self) -> List[Image]:
        db = next(get_db())
        return db.query(Image).filter(Image.source_api == 'wger').all()

    def add_image_to_db(self, term_str: str, img: WgerImage, api_source: str = 'wger'):
        db = next(get_db())
        term_obj = db.query(SearchTerm).filter(SearchTerm.term == term_str).first()

        if not term_obj:
            logger.error(f"Term {term_str} not found in DB")
            return

        # Map WgerImage fields to Image model
        new_image = Image(
            source_id=str(img.id),
            source_api=api_source,
            url_original=img.image,
            url_thumbnail=img.image_thumbnail,
            # Wger images are usually jpg/png, we can infer or default. 
            # The original util treated it as just a string URL.
            # We'll assume jpg or check extension if possible, but default is fine.
            extension="jpg", 
            url_page=f"{self.wger_base_url}/exercise/{img.base_id}/", # Constructing a page URL best effort
            status=ImageStatus.APPROVED.value,
            search_term_id=term_obj.id
        )
        
        try:
            db.add(new_image)
            db.commit()
        except Exception as e:
            logger.error(f"Error adding Wger image to DB: {e}")
            db.rollback()

    def fetch_image(self, id: int) -> Optional[Any]:
        # Implementation depends on if we need to fetch a single image by ID from API
        # The utils had 'get_exercise_image' which fetched by exercise_id.
        # We can implement that logic here if needed, or leave pass if not used by interface yet.
        # But let's implement similar to utils for completeness.
        img_url = f"{self.wger_api_url}/exerciseimage/?exercise={id}&license=1"
        try:
            res = requests.get(img_url).json()
            if res.get('results'):
                # This returns just the image URL in the utils, but fetch_image usually returns an object.
                # For now keeping it consistent with the interface return type hint Any/Optional
                return res['results'][0]
        except Exception as e:
            logger.error(f"Error fetching images from Wger for exercise id '{id}': {e}")
            return None
