import os
import shutil
from flask import Blueprint, request, redirect, url_for, render_template_string
from core.db import get_db
from core.models import Image, SearchTerm, ImageStatus
from utils.common_utils import get_project_folder_as_zip, read_html_as_string
from utils.env_constants import project_name
from utils.log_utils import logger

gallery_bp = Blueprint('gallery', __name__)
GALLERY_PAGE_HTML = read_html_as_string("templates/gallery_page.html")


def image_to_dict(image):
    return {
        'id': image.source_id,
        'api': image.source_api,
        'url_original': image.url_original,
        'url_thumbnail': image.url_thumbnail,
        'url_page': image.url_page,
    }


def get_gallery_data():
    db = next(get_db())
    images = db.query(Image).join(SearchTerm).filter(Image.status == ImageStatus.APPROVED.value).all()
    
    gallery_data = {}
    for img in images:
        term = img.search_term.term
        if term not in gallery_data:
            gallery_data[term] = []

        img_dict = image_to_dict(img)
        gallery_data[term].append(img_dict)

    return gallery_data


@gallery_bp.route('/gallery')
def index():
    gallery_data = get_gallery_data()
    
    return render_template_string(GALLERY_PAGE_HTML,
                                  gallery_data=gallery_data,
                                  project_name=project_name), 200


@gallery_bp.route('/delete-image', methods=['POST'])
def delete_image():
    term = request.form.get('term')
    image_id = request.form.get('imageID')
    api_type = request.form.get('api')
    extension = request.form.get('extension', 'jpg')
    full_file_path_flat = f"assets/{project_name}/image_files/{term}/{image_id}.{extension}"
    
    if os.path.exists(full_file_path_flat):
        os.remove(full_file_path_flat)

    encoded_id = str(image_id)
    db = next(get_db())
    try:
        img_to_delete = db.query(Image).filter(
            Image.source_id == encoded_id,
            Image.source_api == api_type
        ).first()
        
        if img_to_delete:
            db.delete(img_to_delete)
            db.commit()

    except Exception as e:
        logger.error(f"Error deleting image from DB: {e}")
        db.rollback()

    return redirect(url_for('gallery.index'))


@gallery_bp.route('/download-zip')
def download_zip():
    try:
        return get_project_folder_as_zip()
    except Exception as e:
        logger.error(f"Error creating zip file: {e}")
        return redirect(url_for("gallery.index"))
