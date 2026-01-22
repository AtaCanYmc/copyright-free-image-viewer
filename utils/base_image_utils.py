from dataclasses import dataclass
from typing import Optional

from core.state import json_file_path, base_json_file_path
from utils.common_utils import read_json_file, save_json_file


@dataclass
class BaseImage:
    id: str = None
    original: str = None
    thumb: str = None
    api: str = None
    preview: Optional[str] = None
    refresh: Optional[str] = None
    extension: Optional[str] = None


def convert_pexels_photo_to_base(img: dict) -> BaseImage:
    return BaseImage(
        id=img.get('id'),
        api='pexels',
        original=img.get('large'),
        thumb=img.get('small'),
        preview=img.get('url'),
        extension=img.get('extension'),
        refresh=f'https://api.pexels.com/v1/photos/{img.get("id")}'
    )


def convert_pixabay_photo_to_base(img: dict) -> BaseImage:
    return BaseImage(
        id=str(img.get('id')),
        api='pixabay',
        original=img.get('largeImageURL'),
        thumb=img.get('webformatURL'),
        preview=img.get('previewURL'),
        refresh=f'https://pixabay.com/api/?id=${img.get("id")}&key=' + '{0}',
        extension=img.get('extension')
    )


def convert_unsplash_photo_to_base(img: dict) -> BaseImage:
    return BaseImage(
        id=img.get('id'),
        api='unsplash',
        original=img.get('links').get('download'),
        thumb=img.get('links').get('download'),
        preview=img.get('links').get('self'),
        refresh=f'https://api.unsplash.com/photos/${img.get("id")}',
        extension=img.get('extension')
    )


def get_base_images():
    mixed_json = read_json_file(json_file_path)
    base_images = []
    for term, images in mixed_json.items():
        for image in images:
            if image.get('apiType') == 'pexels':
                base_images.append(convert_pexels_photo_to_base(image))
            if image.get('apiType') == 'pixabay':
                base_images.append(convert_pixabay_photo_to_base(image))
            if image.get('apiType') == 'unsplash':
                base_images.append(convert_unsplash_photo_to_base(image))
    return base_images


def base_image_to_json(image: BaseImage):
    return {
        'id': image.id,
        'api': image.api,
        'original': image.original,
        'thumb': image.thumb,
        'preview': image.preview,
        'refresh': image.refresh,
        'extension': image.extension
    }


def save_base_images():
    images = get_base_images()
    json_arr = [base_image_to_json(img) for img in images]
    save_json_file(base_json_file_path, {'images': json_arr})

