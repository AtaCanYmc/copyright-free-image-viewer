import os
from pathlib import Path

from PIL import Image

from utils.env_constants import webp_compression_quality
from utils.log_utils import logger


def convert_to_webp(directory_path, quality=webp_compression_quality):
    """
    Finds images in the given directory AND all subdirectories 
    and converts them to WebP format.
    """
    supported_extensions = [".jpg", ".jpeg", ".png"]
    path = Path(directory_path)

    if not path.is_dir():
        logger.error(f"{directory_path} is not a valid directory.")
        return

    for file in path.rglob("*"):
        if file.suffix.lower() in supported_extensions:
            try:
                with Image.open(file) as img:
                    webp_path = file.with_suffix(".webp")
                    img.save(webp_path, "WEBP", quality=quality)
                    logger.info(f"Converted: {file.relative_to(path)} -> {webp_path.name}")
                    os.remove(file)
            except Exception as e:
                logger.error(f"Failed to convert {file.name}: {e}")

