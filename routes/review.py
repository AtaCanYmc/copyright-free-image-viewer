import os
from typing import Any

from flask import Blueprint, redirect, url_for, render_template_string, request
from core.db import get_db
from core.models import Image, SearchTerm, ImageStatus
from core.session import session
from utils.common_utils import project_name, read_html_as_string, term_to_folder_name, is_download
from utils.log_utils import logger
from utils.common_utils import min_image_for_term

# Import Services
from services.pexels_service import PexelsService
from services.pixabay_service import PixabayService
from services.unsplash_service import UnsplashService
from services.flickr_service import FlickrService
from services.image_service import ImageService

# Instantiate Services
pexels_service = PexelsService()
pixabay_service = PixabayService()
unsplash_service = UnsplashService()
flickr_service = FlickrService()

review_bp = Blueprint('review', __name__)
REVIEW_PAGE_HTML = read_html_as_string("templates/review_page.html")


def get_service_by_api(api_type: str) -> ImageService:
    if api_type == 'pexels':
        return pexels_service
    elif api_type == 'pixabay':
        return pixabay_service
    elif api_type == 'unsplash':
        return unsplash_service
    elif api_type == 'flickr':
        return flickr_service
    else:
        raise ValueError(f"Unknown API type: {api_type}")


def get_url_from_img(photo, api) -> str:
    url = None

    if api == 'pixabay':
        url = photo.largeImageURL
    elif api == 'pexels':
        url = getattr(photo, "large2x", None) or getattr(photo, "original", None)
    elif api == 'unsplash':
        url = getattr(photo.urls, "full", None) or getattr(photo.urls, "regular", None)
        from services.unsplash_service import remove_id_from_img_url
        url = remove_id_from_img_url(url)
    elif api == 'flickr':
        url = getattr(photo, 'hi_res_url', None) or getattr(photo, 'url', None)

    if not url:
        src = getattr(photo, "src", None)
        if isinstance(src, dict):
            url = src.get("large2x") or src.get("original") or next(iter(src.values()), None)

    return url


def get_term_count(term: str) -> int:
    return db.query(Image).filter(
            Image.search_term == term,
            Image.status == ImageStatus.APPROVED.value
        ).count()


def get_current_search_terms():
    db = next(get_db())
    return [t.term for t in db.query(SearchTerm).all()]


def get_photos_for_term_idx(idx, use_cache=True) -> list[Any]:
    terms = get_current_search_terms()
    if idx < 0 or idx >= len(terms):
        return []

    if use_cache and idx in session.photos_cache:
        return session.photos_cache[idx]
    else:
        session.photos_cache[idx] = None

    api_type = session.current_api
    term = terms[idx]
    photos = []

    try:
        service = get_service_by_api(api_type)
        photos = service.search_images(term, per_page=30)
    except Exception as e:
        logger.error(f"Error fetching photos: {e}")
        photos = []

    session.photos_cache[idx] = photos
    return photos


def add_image_to_db(term_str: str, img: Any, api_source: str):
    service = get_service_by_api(api_source)
    service.add_image_to_db(term_str, img, api_source)


def advance_after_action():
    session.photo_idx += 1
    photos = get_photos_for_term_idx(session.term_idx)
    if session.photo_idx >= len(photos):
        session.term_idx += 1
        session.photo_idx = 0


def current_photo_info():
    terms = get_current_search_terms()
    ti = session.term_idx
    pi = session.photo_idx
    cur_api = session.current_api

    if ti >= len(terms):
        return None, None, None, None

    cur_term = terms[ti]
    
    # Count saved images for this term from DB
    db = next(get_db())
    term_obj = db.query(SearchTerm).filter(SearchTerm.term == cur_term).first()
    cur_term_saved_img_count = 0
    if term_obj:
        cur_term_saved_img_count = db.query(Image).filter(
            Image.search_term_id == term_obj.id,
            Image.status == ImageStatus.APPROVED.value
        ).count()

    photos: Any = get_photos_for_term_idx(ti)

    if not photos or pi >= len(photos):
        return cur_term, None, None, cur_term_saved_img_count

    photo = photos[pi]
    url = get_url_from_img(photo, cur_api)
            
    return cur_term, photo, url, cur_term_saved_img_count


def download_image(photo: Any, term: str, force_download=False):
    if not is_download and not force_download:
        return

    c_api = session.current_api
    folder = f"assets/{project_name}/image_files/{term_to_folder_name(term)}"
    service = get_service_by_api(c_api)
    service.download_image(photo, folder)


@review_bp.route('/review')
def index():
    terms = get_current_search_terms()
    
    if not terms:
        return redirect(url_for("setup.index"))
        
    if session.term_idx >= len(terms):
        db = next(get_db())
        total_downloaded = db.query(Image).filter(Image.status == ImageStatus.APPROVED.value).count()
        return render_template_string(REVIEW_PAGE_HTML, finished=True, downloaded=total_downloaded)
        
    term, photo, url, cur_term_saved_img_count = current_photo_info()
    
    finished = False
    if term is None:
        finished = True
        
    db = next(get_db())
    total_downloaded = db.query(Image).filter(Image.status == ImageStatus.APPROVED.value).count()
    
    return render_template_string(
        REVIEW_PAGE_HTML,
        finished=finished,
        term=term,
        term_idx=session.term_idx,
        total_terms=len(terms),
        photo_url=url,
        downloaded=total_downloaded,
        current_api=session.current_api,
        term_photo_counter=cur_term_saved_img_count
    )


@review_bp.route("/decision", methods=["POST"])
def decision():
    action = request.form.get("action")
    
    term, photo, url, cur_term_saved_img_count = current_photo_info()
    logger.debug(f"Decision Execution - Action: {action}, Term: {term}")

    if not term:
        return redirect(url_for("review.index"))

    if action == "previous":
        if session.photo_idx > 0:
            session.photo_idx -= 1
        elif session.term_idx > 0:
            session.term_idx -= 1
            prev_photos = get_photos_for_term_idx(session.term_idx)
            session.photo_idx = max(0, len(prev_photos) - 1)
        return redirect(url_for("review.index"))

    if action == "yes" and photo:
        add_image_to_db(term, photo, session.current_api)
        download_image(photo, term)
        advance_after_action()
        return redirect(url_for("review.index"))

    if action == "no":
        advance_after_action()
        return redirect(url_for("review.index"))

    return redirect(url_for("review.index"))


@review_bp.route("/api-decision", methods=["POST"])
def api_decision():
    action = request.form.get("action")
    
    if action == "use-pexels-api":
        session.photos_cache = {}
        session.current_api = 'pexels'
        session.photo_idx = 0
    elif action == "use-pixabay-api":
        session.photos_cache = {}
        session.current_api = 'pixabay'
        session.photo_idx = 0
    elif action == "use-unsplash-api":
        session.photos_cache = {}
        session.current_api = 'unsplash'
        session.photo_idx = 0
    elif action == "use-flickr-api":
        session.photos_cache = {}
        session.current_api = 'flickr'
        session.photo_idx = 0
        
    return redirect(url_for("review.index"))


@review_bp.route("/term-decision", methods=["POST"])
def term_decision():
    action = request.form.get("action")
    if action == "next-term":
        session.term_idx += 1
        session.photo_idx = 0

    if action == "prev-term":
        if session.term_idx > 0:
            session.term_idx -= 1
            session.photo_idx = 0

    return redirect(url_for("review.index"))


@review_bp.route("/download-all-images", methods=["POST"])
def download_all_images():
    # Placeholder: Bulk download is tricky with current persistent state change to DB.
    # Future enhancement: Implement bulk download from DB.
    return redirect(url_for("review.index"))

@review_bp.route("/download-api-images", methods=["POST"])
def download_api_images():
    # Placeholder
    return redirect(url_for("review.index"))
