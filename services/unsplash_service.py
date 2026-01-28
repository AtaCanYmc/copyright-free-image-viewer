import os
import time
from dataclasses import dataclass, field
from typing import Optional, List
import requests
from dotenv import load_dotenv

from utils.common_utils import get_remote_size, create_folders_if_not_exist
from utils.log_utils import logger

load_dotenv()

@dataclass
class Urls:
    raw: Optional[str] = None
    full: Optional[str] = None
    regular: Optional[str] = None
    small: Optional[str] = None
    thumb: Optional[str] = None
    small_s3: Optional[str] = None

@dataclass
class ProfileImage:
    small: Optional[str] = None
    medium: Optional[str] = None
    large: Optional[str] = None

@dataclass
class UserLinks:
    self_: Optional[str] = None
    html: Optional[str] = None
    photos: Optional[str] = None

@dataclass
class User:
    id: str
    username: str
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    instagram_username: Optional[str] = None
    twitter_username: Optional[str] = None
    portfolio_url: Optional[str] = None
    profile_image: Optional[ProfileImage] = None
    links: Optional[UserLinks] = None

@dataclass
class Links:
    self_: Optional[str] = None
    html: Optional[str] = None
    download: Optional[str] = None

@dataclass
class UnsplashImage:
    id: str
    created_at: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    color: Optional[str] = None
    blur_hash: Optional[str] = None
    description: Optional[str] = None
    alt_description: Optional[str] = None
    urls: Optional[Urls] = None
    links: Optional[Links] = None
    user: Optional[User] = None
    current_user_collections: List[dict] = field(default_factory=list)


def remove_id_from_img_url(url: str) -> str:
    if not url: return ""
    if url.find('?ixid') != -1:
        parts = url.split('?ixid')
    else:
        parts = url.split('&ixid')
    return parts[0] if parts else url

def get_extension_from_url(url: str) -> str:
    if 'fm=' in url:
        return url.split('fm=')[1].split('&')[0]
    return 'jpg'


class UnsplashService:
    def __init__(self):
        self.api_key = os.getenv('UNSPLASH_API_KEY')
        self.api_url = os.getenv("UNSPLASH_API_URL", "https://api.unsplash.com")
        self.max_image_kb = int(os.getenv('MAX_KB_IMAGE_SIZE', '512'))
        
        if not self.api_key:
             logger.warning("UNSPLASH_API_KEY is not set.")

    def _convert_item_to_image(self, item: dict) -> UnsplashImage:
        return UnsplashImage(
            id=item['id'],
            created_at=item.get('created_at'),
            width=item.get('width'),
            height=item.get('height'),
            color=item.get('color'),
            blur_hash=item.get('blur_hash'),
            description=item.get('description'),
            alt_description=item.get('alt_description'),
            urls=Urls(**item['urls']),
            links=Links(
                self_=item['links'].get('self'),
                html=item['links'].get('html'),
                download=item['links'].get('download')
            ),
            user=User(
                id=item['user']['id'],
                username=item['user']['username'],
                name=item['user'].get('name'),
                first_name=item['user'].get('first_name'),
                last_name=item['user'].get('last_name'),
                instagram_username=item['user'].get('instagram_username'),
                twitter_username=item['user'].get('twitter_username'),
                portfolio_url=item['user'].get('portfolio_url'),
                profile_image=ProfileImage(**item['user']['profile_image']),
                links=UserLinks(
                    self_=item['user']['links'].get('self'),
                    html=item['user']['links'].get('html'),
                    photos=item['user']['links'].get('photos')
                )
            ),
            current_user_collections=item.get('current_user_collections', [])
        )

    def search_images(self, query: str, limit: int = 15) -> List[UnsplashImage]:
        if not self.api_key: return []
        
        url = f"{self.api_url}/search/photos"
        params = {
            "query": query,
            "per_page": limit,
            "client_id": self.api_key,
            "order_by": "relevant"
        }

        try:
            response = requests.get(url, params=params)
        except requests.RequestException as e:
            logger.error(f"Error fetching images from Unsplash for query '{query}': {e}")
            return []

        if response.status_code != 200:
            logger.error(f"Error occurred: {response.status_code} - {response.text}")
            return []

        data = response.json()
        return [self._convert_item_to_image(item) for item in data['results']]

    def download_image(self, img: UnsplashImage, folder_path: str) -> bool:
        # Strategy: try full, then regular, then small
        priorities = [img.urls.full, img.urls.regular, img.urls.small]
        
        target_url = None
        content_kb = 0
        
        for url_raw in priorities:
            if not url_raw: continue
            url = remove_id_from_img_url(url_raw)
            image_info = get_remote_size(url)
            kb = image_info.get('kb_decimal', 0)
            
            if kb <= self.max_image_kb:
                target_url = url
                content_kb = kb
                break
        
        if not target_url:
            logger.info(f"Skipped image {img.id} (all sizes exceed {self.max_image_kb} KB)")
            return False

        try:
            image_data = requests.get(target_url, timeout=30)
        except requests.RequestException as e:
            logger.error(f"Error downloading image {img.id} from Unsplash: {e}")
            return False

        extension = get_extension_from_url(target_url)
        image_path = os.path.join(folder_path, f"{img.id}.{extension}")
        create_folders_if_not_exist([folder_path])
        
        with open(image_path, 'wb') as file:
            file.write(image_data.content)
            
        logger.info(f"Downloaded image {img.id} to {image_path} ({content_kb:.2f} KB)")
        return True
