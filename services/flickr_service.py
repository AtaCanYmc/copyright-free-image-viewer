from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import os
import base64
from io import BytesIO

from utils.common_utils import get_remote_size, term_to_folder_name
from utils.log_utils import logger

load_dotenv()

@dataclass
class FlickerImage:
    id: str
    url: str
    hi_res_url: str
    preview: str
    asset_path: str
    base64_data: str

class FlickrService:
    def __init__(self):
        self.scrapper_url = os.getenv('FLICKR_SCRAPPER_URL', 'https://www.flickr.com/search/')
        self.max_image_kb = int(os.getenv('MAX_KB_IMAGE_SIZE', '512'))
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def _convert_image_to_base64(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            image_data = BytesIO(response.content)
            return base64.b64encode(image_data.getvalue()).decode('utf-8')
        except Exception:
            return ""

    def search_images(self, query: str, limit: int = 15) -> list[FlickerImage]:
        params = {
            "text": query,
            "license": "4,5,6,9,10"
        }

        try:
            r = requests.get(self.scrapper_url, params=params, headers=self.headers, timeout=30)
            r.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error fetching images from Flickr for query '{query}': {e}")
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        images = []

        for img in soup.find_all("img"):
            src = img.get("src")
            if not src: continue

            if "staticflickr.com" in src:
                hi_res = re.sub(r"_[a-z]\.jpg", "_b.jpg", src)
                img_id = hi_res.split("/")[-1].split("_")[0]
                
                if any(existing_img.id == img_id for existing_img in images):
                    continue
                    
                images.append(FlickerImage(
                    id=img_id,
                    url=f"https:{src}",
                    hi_res_url=f"https:{hi_res}",
                    asset_path=f"{term_to_folder_name(query)}/{img_id}.jpg",
                    base64_data=self._convert_image_to_base64(f"https:{hi_res}"),
                    preview=''
                ))

        return images[:limit]

    def download_image(self, img: FlickerImage, folder_path: str) -> bool:
        url = img.hi_res_url
        image_info = get_remote_size(url)
        content_kb = image_info.get('kb_decimal', 0)
        
        if content_kb > self.max_image_kb:
            logger.info(f"Skipped image {img.id} ({content_kb:.2f} KB exceeds limit)")
            return False

        try:
            image_data = requests.get(url, timeout=30)
        except requests.RequestException as e:
            logger.error(f"Error downloading image {img.id} from Flickr: {e}")
            return False
            
        extension = url.split('.')[-1]
        image_path = os.path.join(folder_path, f"{img.id}.{extension}")
        
        try:
            with open(image_path, 'wb') as file:
                file.write(image_data.content)
            logger.info(f"Downloaded image {img.id} to {image_path} ({content_kb:.2f} KB)")
            return True
        except Exception as e:
            logger.error(f"Error writing file {image_path}: {e}")
            return False
