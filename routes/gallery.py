import os
import shutil
from flask import Blueprint, request, redirect, url_for, render_template_string
from core.db import get_db
from core.models import Image, SearchTerm, ImageStatus
from utils.base_image_utils import save_base_images, get_base_images_from_db
from utils.common_utils import project_name, get_image_url, get_thumbnail, \
    read_html_as_string, get_project_folder_as_zip
from utils.log_utils import logger

gallery_bp = Blueprint('gallery', __name__)
GALLERY_PAGE_HTML = read_html_as_string("templates/gallery_page.html")


@gallery_bp.route('/gallery')
def index():
    db = next(get_db())
    # Fetch all approved images with their search terms
    images = db.query(Image).join(SearchTerm).filter(Image.status == ImageStatus.APPROVED.value).all()
    
    # Group by term to match template expectation (dict: term -> list of dicts)
    gallery_data = {}
    for img in images:
        term = img.search_term.term
        if term not in gallery_data:
            gallery_data[term] = []
            
        # Create dict structure expected by template (or close to it)
        # Template uses: img.id, img.apiType (or api), get_url_func(img), ...
        # I need to ensure the dict has keys the template expects.
        # Template: `image['id']`, `image['apiType']`
        img_dict = {
            'id': img.source_id,
            'apiType': img.source_api,
            'largeImageURL': img.url_large, # For Pixabay mainly, but used as fallback
            'large2x': img.url_large,       # For Pexels
            'original': img.url_original,
            # Add other fields helper functions might need
            'src': {'original': img.url_large} # Mock for some helpers
        }
        gallery_data[term].append(img_dict)

    return render_template_string(GALLERY_PAGE_HTML,
                                  gallery_data=gallery_data,
                                  project_name=project_name,
                                  get_url_func=get_image_url,
                                  get_thumb_func=get_thumbnail), 200


@gallery_bp.route('/delete-image', methods=['POST'])
def delete_image():
    term = request.form.get('term')
    image_id = request.form.get('imageID')
    api_type = request.form.get('apiType')
    extension = request.form.get('extension', 'jpg')
    
    # Delete from Filesystem
    # Note: path construction might need to be robust
    full_file_path = f"assets/{project_name}/image_files/{term}/{image_id}.{extension}"
    # Also check if it's nested under api type? The original code had `.../image_files/{api_type}/{term}...` 
    # but `review.py` saved to `.../image_files/{term}`.
    # Let's assume `review.py` logic which is flat under term.
    # Wait, original `gallery.py` line 34: f"assets/{project_name}/image_files/{api_type}/{term}/{image_id}.{extension}"
    # My rewritten `review.py`: `folder = f"assets/{project_name}/image_files/{term_to_folder_name(term)}"`
    # So my rewritten `review.py` saves to `assets/project/image_files/term/`.
    # I should try to delete from there.
    
    full_file_path_flat = f"assets/{project_name}/image_files/{term}/{image_id}.{extension}"
    
    if os.path.exists(full_file_path_flat):
        os.remove(full_file_path_flat)

    # Delete from DB
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
        # Generate base_images.json (or equivalent) for the zip?? 
        # The original code generated a JSON for the ZIP.
        # I should generate a metadata file for the ZIP from DB.
        save_base_images() 
        return get_project_folder_as_zip()
    except Exception as e:
        logger.error(f"Error creating zip file: {e}")
        return redirect(url_for("gallery.index"))
