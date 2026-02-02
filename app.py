import webbrowser
from threading import Timer

from flask import Flask, render_template_string

from core.db import get_db, init_db
from core.models import Image, ImageStatus, SearchTerm
from routes.explorer import explorer_bp
from routes.gallery import gallery_bp
from routes.review import review_bp
from routes.settings import settings_bp
from routes.setup import setup_bp
from utils.common_utils import create_folders_if_not_exist, delete_files_if_exist, read_html_as_string
from utils.env_constants import app_host, app_port, project_name, use_debug_mode, use_reloader

# Initialize Database
init_db()

# Create necessary folders (keep assets for downloaded images)
create_folders_if_not_exist([
    "assets",
    "assets/zip_files",
    f"assets/{project_name}",
    f"assets/{project_name}/image_files",
    f"assets/{project_name}/json_files",
    f"assets/{project_name}/csv_files",
    f"assets/{project_name}/log_files"
])

# Clean up temporary files
delete_files_if_exist("assets/zip_files")

api_list = ['pexels', 'pixabay', 'unsplash', 'flickr']

ERROR_PAGE_HTML = read_html_as_string("templates/error_page.html")
HOME_PAGE_HTML = read_html_as_string("templates/home_page.html")

pages = [
    {'name': 'home', 'route': '/'},
    {'name': 'settings', 'route': '/settings'},
    {'name': 'setup', 'route': '/setup'},
    {'name': 'review', 'route': '/review'},
    {'name': 'gallery', 'route': '/gallery'},
    {'name': 'explorer', 'route': '/explorer'}
]

app = Flask(__name__)
app.register_blueprint(review_bp)
app.register_blueprint(gallery_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(setup_bp)
app.register_blueprint(explorer_bp)


@app.route('/health')
def health_check():
    return {"status": "ok"}, 200


@app.route('/')
def home():
    db = next(get_db())
    total_terms = db.query(SearchTerm).count()
    downloaded = db.query(Image).filter(Image.status == ImageStatus.APPROVED.value).count()

    return render_template_string(HOME_PAGE_HTML,
                                  project_name=project_name,
                                  total_terms=total_terms,
                                  downloaded=downloaded)


@app.context_processor
def inject_pages():
    return dict(pages=pages)


@app.errorhandler(404)
def page_not_found(e):
    return (render_template_string(ERROR_PAGE_HTML,
                                   error_code="404",
                                   error_title="Page Not Found",
                                   error_message="The page you are looking for may have been moved or deleted."),
            404)


@app.errorhandler(500)
def internal_server_error(e):
    return (render_template_string(ERROR_PAGE_HTML,
                                   error_code="500",
                                   error_title="Internal Server Error",
                                   error_message="An unexpected issue occurred on the server side. " +
                                                 "Please check your code."),
            500)


def open_browser():
    url_host = app_host if app_host != '0.0.0.0' else 'localhost'
    webbrowser.open_new(f"http://{url_host}:{app_port}/")


if __name__ == "__main__":
    Timer(2, open_browser).start()
    app.run(
        host=app_host,
        port=app_port,
        debug=use_debug_mode,
        use_reloader=use_reloader
    )
