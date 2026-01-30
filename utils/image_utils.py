import os
from pathlib import Path
from PIL import Image
from utils.env_constants import webp_compression_quality
from utils.log_utils import logger

def convert_to_webp(directory_path, quality=webp_compression_quality):
    """
    Finds images in the given directory and converts them to WebP format.
    :param directory_path: Path to the folder containing images.
    :param quality: Compression quality (1-100).
    """
    supported_extensions = [".jpg", ".jpeg", ".png"]
    path = Path(directory_path)

    if not path.is_dir():
        logger.error(f"{directory_path} is not a valid directory.")
        return

    for file in path.iterdir():
        if file.suffix.lower() in supported_extensions:
            try:
                with Image.open(file) as img:
                    webp_path = file.with_suffix(".webp")
                    img.save(webp_path, "WEBP", quality=quality)
                    logger.info(f"Converted: {file.name} -> {webp_path.name}")
                    os.remove(file)
            except Exception as e:
                logger.error(f"Failed to convert {file.name}: {e}")

