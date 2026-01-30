import os

import requests
from dotenv import load_dotenv

from core.models import Image
from utils.common_utils import create_folders_if_not_exist
from utils.env_constants import max_image_kb
from utils.log_utils import logger

load_dotenv()


def get_remote_size(url: str) -> dict:
    try:
        head = requests.head(url, timeout=10)
        cl = head.headers.get('Content-Length')
        if cl:
            size_bytes = int(cl)
            return {
                'bytes': size_bytes,
                'kb_decimal': size_bytes / 1000 if size_bytes > 0 else 0,
                'kb_binary': size_bytes / 1024 if size_bytes > 0 else 0,
                'source': 'Content-Length header'
            }
    except Exception as e:
        logger.error(f'Failed to get size of {url}. {e}')
        pass

    size = 0
    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            for chunk in r.iter_content(8192):
                if chunk:
                    size += len(chunk)
    except Exception as e:
        logger.error(f"Could not determine size for URL: {url}. {e}")
        pass

    return {
        'bytes': size,
        'kb_decimal': size / 1000 if size > 0 else 0,
        'kb_binary': size / 1024 if size > 0 else 0,
        'source': 'streamed download'
    }



def download_image(img: Image, folder_path: str, max_kb: int = max_image_kb):
   url = img.url_original
   if not url:
       return False

   try:
     image_info = get_remote_size(url)
     content_kb = image_info.get('kb_decimal', 0)
     if content_kb > max_kb:
         logger.warning(f"Image {img.source_id} from {img.source_api} is larger than {max_kb} KB")
         return False
     image_data = requests.get(url, timeout=30)
   except requests.RequestException as e:
       logger.error(f"Error downloading image {img.source_id} from {img.source_api}: {e}")
       return False

   image_path = os.path.join(folder_path, f"{img.source_id}.{img.extension}")
   create_folders_if_not_exist([folder_path])

   with open(image_path, 'wb') as file:
       file.write(image_data.content)

   logger.info(f"Downloaded image {img.source_id} to {image_path} ({content_kb:.2f} KB)")
   return True
