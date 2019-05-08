import logging
import os
import shutil
from datetime import datetime
from os.path import join

import requests
import trimesh
import wget
from tqdm import tqdm
from trimesh.exchange.export import export_mesh

import db
from config import scrap_path
from utils import make_dir

grapcad_url = 'https://grabcad.com'
api_url = f'{grapcad_url}/community/api/v1/models'
login_url = f'{grapcad_url}/login'
sw_ext_mapping = {
    'stl': '.stl',
    'obj': '.obj',
    'ptc-creo-parametric': '.prt',
    'solidworks': '.sldprt',
}


def search(keyword, softwares, page=1, per_page=100, sort='following', time='all_time'):
    payload = {
        'page': str(page),
        'per_page': str(per_page),
        'query': keyword,
        'softwares': softwares,
        'sort': sort,
        'time': time,
    }
    r = requests.post(api_url, data=payload)
    if r.status_code == 200:
        result = []
        for item in r.json()['models']:
            result.append(item['cached_slug'])
        return result, r.json()['total_entries']
    else:
        raise ConnectionError


def get_model_names(keyword, softwares=None):
    if softwares is None:
        softwares = ["obj"]
    per_page = 100
    model_names, total_models = search(keyword, per_page=per_page, softwares=softwares)
    for i in tqdm(range(total_models // per_page)):
        model_name, _ = search(keyword, page=i + 2, softwares=softwares)
        model_names += model_name
    return model_names


def get_cadid(cached_slug):
    url = f'{api_url}/{cached_slug}'
    r = requests.get(url)
    if r.status_code == 200:
        if 'archive_url' in r.json():
            return r.json()['archive_url'].split('=')[-1]
        else:
            return None
    else:
        raise ConnectionError


def download_zipfile(cadid, output_dir):
    url = f'https://d2t1xqejof9utc.cloudfront.net/cads/files/{cadid}/original.zip'
    return wget.download(url, out=output_dir)


def unzip_file(zip_file, output_dir=None):
    if not output_dir:
        output_dir = zip_file.replace('.zip', '')

    # import zipfile
    # zip_ref = zipfile.ZipFile(zip_file, 'r')
    # zip_ref.extractall()
    # zip_ref.close()
    os.system(f'unzip -o {zip_file} -d {output_dir}')
    os.remove(zip_file)
    return output_dir


def filter_files(keyword, unzipped_dir, softwares):
    formats = [sw_ext_mapping[software] for software in softwares]

    files = []
    for file in os.listdir(unzipped_dir):
        filename, ext = os.path.splitext(file)
        if (ext.lower() in formats) and (keyword in filename.lower()):
            files.append(file)

    return files


def move_file(file, dst_dir):
    basename = os.path.basename(file)
    head, tail = os.path.splitext(basename)
    dst_file = os.path.join(dst_dir, basename)

    count = 0
    while os.path.exists(dst_file):
        count += 1
        dst_file = os.path.join(dst_dir, '%s-%d%s' % (head, count, tail))

    shutil.move(file, dst_file)
    return dst_file


def convert_to_obj(file):
    basename = os.path.basename(file)
    filename, ext = os.path.splitext(basename)
    if ext.lower() != '.obj':
        mesh = trimesh.load_mesh(file)
        obj_file = file.replace(ext, '.obj')
        export_mesh(mesh, obj_file, file_type='obj')
        os.remove(file)
        return obj_file
    else:
        return file


def insert_search_log(keyword, softwares):
    return db.insert('search_log', **{'keyword': keyword, 'softwares': ';'.join(softwares)})


def insert_search_result(model_name, search_id):
    return db.insert('search_results', **{'model_name': model_name, 'search_id': search_id})


def insert_grabcad_model(model_name, cadid):
    return db.insert('grabcad_model', ignore=True, **{'model_name': model_name, 'cadid': cadid})


def insert_grabcad_file(cadid, filepath):
    return db.insert('grabcad_files', ignore=True, **{'cadid': cadid, 'file': filepath})


def is_model(model_name):
    return not db.query(f"SELECT * from grabcad_files WHERE model_name='{model_name}'").empty


def scrap(keyword, limit=0, softwares=None):
    keyword = keyword.lower()
    print(keyword)
    if softwares is None:
        softwares = ['obj', 'stl']

    output_dir = f'{scrap_path}/{keyword}'
    make_dir(output_dir)

    # search models
    model_names = get_model_names(keyword, softwares=softwares)
    search_id = insert_search_log(keyword, softwares)

    if limit:
        limit = min(limit, len(model_names))

    print(f'{len(model_names)} models found.')

    no_model = 0
    for model_name in tqdm(model_names):

        # filter by model name
        if keyword not in model_name.lower():
            continue

        # check db
        if is_model(model_name):
            insert_search_result(model_name, search_id)
            continue

        # check model validity
        cadid = get_cadid(model_name)
        if not cadid:
            continue
        insert_grabcad_model(model_name, cadid)
        insert_search_result(model_name, search_id)

        # unzip model
        zip_file = download_zipfile(cadid, output_dir)
        unzipped_dir = unzip_file(zip_file)

        # extract files with valid extension
        files = filter_files(keyword, unzipped_dir, softwares)
        if not files:
            shutil.rmtree(unzipped_dir)
            continue

        # move valid files
        for file in files:
            moved_file = move_file(join(unzipped_dir, file), output_dir)
            obj_file = convert_to_obj(moved_file)
            insert_grabcad_file(cadid, obj_file)
            no_model += 1

        # remove unzipped directory
        shutil.rmtree(unzipped_dir)

        # stop if enough models
        if limit and no_model > limit:
            break


if __name__ == "__main__":
    keywords = db.query('SELECT name FROM labels where use=TRUE')
    logging.basicConfig(filename=f'{datetime.now().strftime("%y%m%d_%H%M%S")}.log', level=logging.DEBUG)

    for idx, keyword in keywords.iterrows():
        try:
            scrap(keyword=keyword['name'], softwares=['obj', 'stl'])
        except Exception as e:
            logging.debug(f'[{keyword}]:{e}')
            continue
    # scrap(keyword='bolts', softwares=['obj', 'stl'])
    # unzip_file('/mnt/4TWD/grabCAD/bolts/cluster-of-bolts.zip')
