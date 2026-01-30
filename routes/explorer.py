import os
import shutil
from flask import Blueprint, render_template_string, jsonify
from utils.common_utils import read_html_as_string, get_directory_tree, save_json_file
from utils.env_constants import project_name
from utils.image_utils import convert_to_webp
from utils.log_utils import logger
from factory.image_service_factory import ImageServiceFactory
from core.db import get_db, get_query_as_json
from core.models import Image

explorer_bp = Blueprint('explorer', __name__)
EXPLORER_PAGE_HTML = read_html_as_string("templates/explorer_page.html")


@explorer_bp.route('/explorer')
def explorer():
    root_path = os.path.join('assets', project_name)
    tree_data = get_directory_tree(root_path) if os.path.exists(root_path) else {}
    return render_template_string(
        EXPLORER_PAGE_HTML,
        tree_data=tree_data,
        project_name=project_name
    )

@explorer_bp.route('/explorer/actions/convert-webp', methods=['POST'])
def convert_webp_action():
    try:
        images_path = os.path.join('assets', project_name, 'image_files')
        logger.info(f"Converting images in {images_path} to WebP...")
        convert_to_webp(images_path)
        return jsonify({"status": "success", "message": "Conversion started/completed."})
    except Exception as e:
        logger.error(f"Error converting to webp: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@explorer_bp.route('/explorer/actions/convert-db-json', methods=['POST'])
def convert_db_json_action():
    try:
        logger.info(f"Converting images in database to JSON...")
        query = "SELECT i.*, st.term FROM images i JOIN search_terms st ON i.search_term_id = st.id"
        json_data = get_query_as_json(query)
        file_path = os.path.join('assets', project_name, 'json_files', 'images.json')
        save_json_file(file_path, json_data)
        return jsonify({"status": "success", "message": "Conversion started/completed."})
    except Exception as e:
        logger.error(f"Error converting to json: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@explorer_bp.route('/explorer/actions/refetch/<api_source>', methods=['POST'])
def refetch_action(api_source):
    try:
        logger.info(f"Refetching images from {api_source}...")
        service = ImageServiceFactory.get_service(api_source)
        db = next(get_db())
        api_images = db.query(Image).filter(Image.api_source == api_source).all()
        
        for img in api_images:
            new_img = service.fetch_image(img.source_id)
            service.update_image_in_db(new_img)
                
        return jsonify({"status": "success", "message": f"Refetched {len(api_images)} images from {api_source}."})
    except Exception as e:
        logger.error(f"Error refetching from {api_source}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@explorer_bp.route('/explorer/actions/delete-images', methods=['POST'])
def delete_images_action():
    try:
        images_path = os.path.join('assets', project_name, 'image_files')
        if os.path.exists(images_path):
            shutil.rmtree(images_path)
            os.makedirs(images_path, exist_ok=True)
            logger.info("Deleted all images in assets folder.")
            return jsonify({"status": "success", "message": "All images deleted."})
        return jsonify({"status": "success", "message": "Images folder not found."})
    except Exception as e:
        logger.error(f"Error deleting images: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@explorer_bp.route('/explorer/actions/delete-db', methods=['POST'])
def delete_db_action():
    try:
        db = next(get_db())
        db.query(Image).delete()
        db.commit()
        logger.info("Deleted all images from database.")
        return jsonify({"status": "success", "message": "All images deleted from database."})
    except Exception as e:
        logger.error(f"Error deleting images from database: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

