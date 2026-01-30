import csv
import json
import os
import shutil
from threading import Timer

from flask import Response, send_file

from utils.log_utils import logger


def term_to_folder_name(term: str) -> str:
    return term.replace(' ', '_').lower()


def create_folders_if_not_exist(folder_names: list[str]):
    for folder_name in folder_names:
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)


def create_files_if_not_exist(file_paths: list[str]):
    for file_path in file_paths:
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write('')


def read_html_as_string(file_path: str) -> str:
    with open(file_path, encoding='utf-8') as file:
        return file.read()


def read_json_file(file_path: str) -> dict:
    with open(file_path, encoding='utf-8') as file:
        return json.load(file)


def save_json_file(file_path: str, data: dict):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def save_csv_file(file_path: str, data: list[dict]):
    with open(file_path, 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data[0].keys())
        for item in data:
            writer.writerow(item.values())


def delete_file_if_exists(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"Deleted file {file_path}")


def delete_files_if_exist(folder_path: str):
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)


def get_directory_tree(path):
    d = {'name': os.path.basename(path), 'type': 'folder', 'children': []}
    try:
        for entry in os.scandir(path):
            if entry.is_dir():
                d['children'].append(get_directory_tree(entry.path))
            else:
                d['children'].append({'name': entry.name, 'type': 'file'})
    except PermissionError:
        pass
    return d


def get_project_folder_as_zip() -> tuple[Response, int]:
    source_dir = f"assets/{project_name}"
    zip_filename = f"{project_name}_assets"
    zip_path = f"assets/zip_files/{zip_filename}"

    shutil.make_archive(zip_path, 'zip', source_dir)
    # delete the zip file after 120 seconds
    Timer(120, delete_file_if_exists, args=[f"{zip_path}.zip"]).start()
    return send_file(f"{zip_path}.zip", as_attachment=True), 200
