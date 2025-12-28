import os
import requests
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

pixabay_api_key = os.getenv('PIXABAY_API_KEY')
pixabay_api_url = os.getenv('PIXABAY_API_URL')


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
    favorites: int
    likes: int
    comments: int
    user_id: int
    user: str
    userImageURL: str


def get_image_from_pixabay(term, page_idx=1, results_per_page=15) -> list[PixabayImage]:
    params = {
        'key': pixabay_api_key,
        'q': term,
        'page': page_idx,
        'per_page': results_per_page,
        'image_type': 'photo',
    }
    response = requests.get(pixabay_api_url, params=params)
    data = response.json()
    return data.get('hits', [])
