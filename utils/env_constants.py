import os
import sys
import uuid
import argparse
from dotenv import load_dotenv

load_dotenv()


# Detect if running under pytest
if "pytest" in sys.modules or os.path.basename(sys.argv[0]) in ["pytest", "py.test"]:
    project_name = "test_project"
else:
    parser = argparse.ArgumentParser(description='Image Generator')
    parser.add_argument('project_name', type=str, nargs='?', default=f'project_{str(uuid.uuid4())[:8]}', help='Project name')
    args, _ = parser.parse_known_args()
    project_name = args.project_name

min_image_for_term = int(os.getenv('MIN_IMAGES_PER_TERM', '1'))
is_download = os.getenv('DOWNLOAD_IMAGES', 'false').lower() == 'true'
app_port = os.getenv('APP_PORT', '8080')
app_host = os.getenv('APP_HOST', '0.0.0.0')
use_debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
use_reloader = os.getenv('USE_RELOADER', 'false').lower() == 'true'
max_image_kb = int(os.getenv('MAX_KB_IMAGE_SIZE', '512'))
