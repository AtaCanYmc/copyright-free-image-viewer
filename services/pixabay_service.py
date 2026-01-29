from typing import List, Optional, Dict, Any, Tuple
import os
import requests
from dataclasses import dataclass
from dotenv import load_dotenv
from services.image_service import ImageService
from utils.common_utils import get_remote_size, create_folders_if_not_exist
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


    def json_to_image(self, item: Dict[str, Any]) -> PixabayImage:
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


    def search_images(self, term: str, page: int = 1, per_page: int = 15) -> List[PixabayImage]:
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


    def is_response_expired(self, response: requests.Response) -> bool:
        content_str = response.text.lower()
        return 'invalid' in content_str or 'expired' in content_str


    def find_download_url(self, img: PixabayImage) -> Tuple[Optional[str], float]:
        url = img.largeImageURL
        image_info = get_remote_size(url)
        content_kb = image_info.get('kb_decimal', 0)
        
        if content_kb > self.max_image_kb:
            logger.info(f"Skipped image {img.id} ({content_kb:.2f} KB exceeds limit)")
            return None, None

        return url, content_kb


    def download_image(self, img: PixabayImage, folder_path: str) -> bool:
        url, content_kb = self.find_download_url(img)
        if not url:
            return False

        try:
            response = requests.get(url, timeout=30)
            if self.is_response_expired(response):
                logger.error(f"URL invalid/expired: {url}")
                return False
                 
            extension = url.split('.')[-1]
            image_path = os.path.join(folder_path, f"{img.id}.{extension}")
            create_folders_if_not_exist([folder_path])
            
            with open(image_path, 'wb') as file:
                file.write(response.content)
            
            logger.info(f"Downloaded image {img.id} to {image_path} ({content_kb:.2f} KB)")
            return True
        except Exception as e:
            logger.error(f"Error downloading image {img.id} from Pixabay: {e}")
            return False


    def add_image_to_db(self, term_str: str, img: Any, api_source: str):
        db = next(get_db())
        term_obj = db.query(SearchTerm).filter(SearchTerm.term == term_str).first()

        if not term_obj:
            logger.error(f"Term {term_str} not found in DB")
            return

        img_id = str(getattr(img, 'id', 'unknown'))
        url_large = getattr(img, "largeImageURL", None)
        url_thumbnail = getattr(img, "previewURL", None)

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
