import os
from dataclasses import dataclass, field
from typing import Optional, List, Any
import requests
from dotenv import load_dotenv
from core.db import get_db
from core.models import Image, ImageStatus, SearchTerm
from services.image_service import ImageService
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


class UnsplashService(ImageService):
    def __init__(self):
        self.api_key = os.getenv('UNSPLASH_API_KEY')
        self.api_url = os.getenv("UNSPLASH_API_URL", "https://api.unsplash.com")
        self.max_image_kb = int(os.getenv('MAX_KB_IMAGE_SIZE', '512'))
        
        if not self.api_key:
             logger.warning("UNSPLASH_API_KEY is not set.")


    def json_to_image(self, item: dict) -> UnsplashImage:
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


    def get_all_images(self) -> list[Image]:
        db = next(get_db())
        return db.query(Image).filter(Image.source_api == 'unsplash').all()


    def search_images(self, query: str, per_page: int = 15) -> List[UnsplashImage]:
        if not self.api_key: return []
        
        url = f"{self.api_url}/search/photos"
        params = {
            "query": query,
            "per_page": per_page,
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
        return [self.json_to_image(item) for item in data['results']]


    def add_image_to_db(self, term_str: str, img: Any, api_source: str):
        db = next(get_db())
        term_obj = db.query(SearchTerm).filter(SearchTerm.term == term_str).first()

        if not term_obj:
            logger.error(f"Term {term_str} not found in DB")
            return

        img_id = str(getattr(img, 'id', 'unknown'))
        links = getattr(img, "links", None)
        url_original = getattr(links, "download", None)
        url_thumbnail = getattr(links, "download", None)
        url_page = getattr(links, "html", None)
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
