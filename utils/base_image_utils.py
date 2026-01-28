from dataclasses import dataclass
from typing import Optional
import json
import os

# import from db instead of json file
from core.db import get_db
from core.models import Image, SearchTerm, ImageStatus
from utils.common_utils import save_json_file, project_name

@dataclass
class BaseImage:
    id: str = None
    original: str = None
    thumb: str = None
    api: str = None
    preview: Optional[str] = None
    refresh: Optional[str] = None
    extension: Optional[str] = None


def convert_db_image_to_base(img: Image) -> BaseImage:
    # Logic to map DB columns to BaseImage
    # This might need some reconstruction of URLs if they aren't fully stored
    return BaseImage(
        id=img.source_id,
        api=img.source_api,
        original=img.url_large,
        thumb=img.url_thumbnail or img.url_large,
        preview=img.url_large,
        # extension could be derived
        extension="jpg" # Default or derive
    )

def get_base_images_from_db():
    db = next(get_db())
    images = db.query(Image).filter(Image.status == ImageStatus.APPROVED.value).all()
    return [convert_db_image_to_base(img) for img in images]

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
    images = get_base_images_from_db()
    json_arr = [base_image_to_json(img) for img in images]
    # We still save this JSON because it might be needed for the ZIP export
    base_json_path = f"assets/{project_name}/json_files/base_images.json"
    os.makedirs(os.path.dirname(base_json_path), exist_ok=True)
    save_json_file(base_json_path, {'images': json_arr})
