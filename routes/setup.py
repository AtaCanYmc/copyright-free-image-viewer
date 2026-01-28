from flask import Blueprint, request, redirect, url_for, render_template_string
from utils.common_utils import read_html_as_string, project_name

setup_bp = Blueprint('setup', __name__)
TXT_SETUP_PAGE_HTML = read_html_as_string("templates/txt_setup_page.html")


from core.db import get_db
from core.models import SearchTerm

@setup_bp.route("/setup", methods=['GET', 'POST'])
def index():
    db = next(get_db())
    
    if request.method == 'POST':
        content = request.form.get('terms', '')
        # Clear existing terms or update? Simplest is to clear and replace for this logic, 
        # or just add new ones. The original code overwrote the file. 
        # So we will delete all and re-add to match original behavior, or smart update.
        # Let's simple overwrite for now to match behavior.
        
        # Parse terms
        new_term_strings = [t.strip() for t in content.split('\n') if t.strip()]
        
        # Transactional update
        try:
            db.query(SearchTerm).delete()
            for term_str in new_term_strings:
                term = SearchTerm(term=term_str)
                db.add(term)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
            
        return redirect(url_for("review.index"))

    # Fetch existing terms
    terms = db.query(SearchTerm).all()
    term_strings = [t.term for t in terms]

    return render_template_string(
        TXT_SETUP_PAGE_HTML,
        project_name=project_name,
        terms="\n".join(term_strings)
    )
