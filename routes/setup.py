from flask import Blueprint, request, redirect, url_for, render_template_string
from utils.common_utils import read_html_as_string
from utils.env_constants import project_name
from core.db import get_db
from core.models import SearchTerm
from core.session import session

setup_bp = Blueprint('setup', __name__)
TXT_SETUP_PAGE_HTML = read_html_as_string("templates/txt_setup_page.html")

def update_terms(content: str):
    db = next(get_db())
    new_term_strings = [t.strip() for t in content.split('\n') if t.strip()]
    
    try:
        db.query(SearchTerm).delete()
        for term_str in new_term_strings:
            term = SearchTerm(term=term_str)
            db.add(term)
        db.commit()
        session.reset_photo_idx()
        session.clear_cache()
    except Exception as e:
        db.rollback()
        raise e


@setup_bp.route("/setup", methods=['GET', 'POST'])
def index():
    db = next(get_db())
    
    if request.method == 'POST':
        content = request.form.get('terms', '')
        update_terms(content)
        return redirect(url_for("review.index"))
        
    terms = db.query(SearchTerm).all()
    term_strings = [t.term for t in terms]

    return render_template_string(
        TXT_SETUP_PAGE_HTML,
        project_name=project_name,
        terms="\n".join(term_strings)
    )
