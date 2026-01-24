import os

from flask import Blueprint, render_template_string

from utils.common_utils import read_html_as_string, get_directory_tree, project_name

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
