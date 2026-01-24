import os
from typing import Optional

import requests
from dotenv import load_dotenv
from dataclasses import dataclass

from core.state import json_file_path
from utils.common_utils import get_remote_size, read_json_file, create_folders_if_not_exist, change_image_in_json
from utils.log_utils import logger

load_dotenv()

pixabay_api_key = os.getenv('PIXABAY_API_KEY')
pixabay_api_url = os.getenv('PIXABAY_API_URL')
if not pixabay_api_key or not pixabay_api_url:
    raise EnvironmentError(
        "Environment variables `PIXABAY_API_KEY` "
        "or `PIXABAY_API_URL` are not set. Set them in the environment or in a `.env` file.")
max_image_kb = int(os.getenv('MAX_KB_IMAGE_SIZE', '512'))


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


def get_extension_from_url(url: str):
    return url.split('.')[-1]


def get_image_from_pixabay(term, page_idx=1, results_per_page=15) -> list[PixabayImage]:
    params = {
        'key': pixabay_api_key,
        'q': term,
        'page': page_idx,
        'per_page': results_per_page,
        'image_type': 'photo',
    }

    try:
        response = requests.get(pixabay_api_url, params=params, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error fetching images from Pixabay for term '{term}': {e}")
        return []

    data = response.json()
    if 'error' in data:
        raise Exception(f"Pixabay API error: {data['error']}")
    image_list = []
    for item in data.get('hits', []):
        img = convert_json_to_pixabay_image(item)
        image_list.append(img)
    return image_list


def convert_json_to_pixabay_image(item: dict) -> PixabayImage:
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


def refetch_pixabay_image(image_id: int) -> Optional[PixabayImage]:
    url = pixabay_api_url
    params = {
        'key': pixabay_api_key,
        'id': image_id
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("hits") and len(data["hits"]) > 0:
            image_data = data["hits"][0]
            pix_img = convert_json_to_pixabay_image(image_data)
            change_image_in_json(json_file_path, image_id, convert_pixabay_image_to_json(pix_img))
            return convert_json_to_pixabay_image(image_data)

        return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Connection error: {e}")
        return None
    except TypeError as e:
        logger.error(f"Veri eşleştirme hatası (Sınıf yapısı API ile uyumsuz olabilir): {e}")
        return None


def download_pixabay_images(image_list: list[PixabayImage], folder_name: str):
    for img in image_list:
        download_pixabay_image(img, folder_name)


def download_pixabay_image(img: PixabayImage, folder_name: str, refetch: bool = False):
    url = img.largeImageURL
    image_info = get_remote_size(url)
    content_kb = image_info.get('kb_decimal', 0)
    if content_kb <= max_image_kb:
        try:
            response = requests.get(url, timeout=30)
            content_str = response.text.lower()
            if 'invalid' in content_str or 'expired' in content_str:
                raise ValueError(f"This URL is invalid or has expired: {url}")
        except Exception as e:
            logger.error(f"Error downloading image {img.id} from Pixabay: {e}")
            if not refetch:
                new_img = refetch_pixabay_image(img.id)
                if new_img:
                    download_pixabay_image(new_img, folder_name, refetch=True)
            return

        extension = get_extension_from_url(url)
        image_path = os.path.join(folder_name, f"{img.id}.{extension}")
        create_folders_if_not_exist([folder_name])
        with open(image_path, 'wb') as file:
            file.write(response.content)
        logger.info(f"Downloaded image {img.id} to {image_path} ({content_kb:.2f} KB)")
    else:
        logger.info(f"Skipped image {img.id} ({content_kb:.2f} KB exceeds limit)")


def convert_pixabay_image_to_json(img: PixabayImage) -> dict:
    return {
        'id': img.id,
        'pageURL': img.pageURL,
        'type': img.type,
        'tags': img.tags,
        'previewURL': img.previewURL,
        'previewWidth': img.previewWidth,
        'previewHeight': img.previewHeight,
        'webformatURL': img.webformatURL,
        'webformatWidth': img.webformatWidth,
        'webformatHeight': img.webformatHeight,
        'largeImageURL': img.largeImageURL,
        'imageWidth': img.imageWidth,
        'imageHeight': img.imageHeight,
        'imageSize': img.imageSize,
        'views': img.views,
        'downloads': img.downloads,
        'likes': img.likes,
        'comments': img.comments,
        'user_id': img.user_id,
        'user': img.user,
        'userImageURL': img.userImageURL,
        'extension': get_extension_from_url(img.largeImageURL or img.webformatURL or img.previewURL),
        'apiType': 'pixabay'
    }


def download_pixabay_images_from_json(json_file: str, folder_name: str):
    json_data = read_json_file(json_file)

    for term, images in json_data.items():
        pixabay_images = [convert_json_to_pixabay_image(img_data) for img_data in images if
                          img_data.get('apiType') == 'pixabay']
        folder_path = os.path.join(folder_name, term)
        download_pixabay_images(pixabay_images, folder_path)
