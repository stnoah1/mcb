import logging
import os
import shutil
from os.path import join

import requests
import wget
from tqdm import tqdm

import db
from create_img import create_image
from utils import make_dir, clean_dir
from config import dw_path
from scrapper.base import filter_escape_char, unzip_file, move_file, convert_to_obj

url = 'https://3dwarehouse.sketchup.com/warehouse/v1.0/entities'


def search(keyword, per_search=100, offset=0):
    payload = {
        'count': per_search,
        'recordEvent': 'false',
        'q': keyword,
        'fq': 'attribute:categories:domain:string=="Industrial";binaryNames=exists=true',
        'showBinaryMetadata': 'true',
        'showAttributes': 'false',
        'showBinaryAttributes': 'true',
        'offset': offset,
        'contentType': '3dw',
    }

    r = requests.get(url, params=payload)

    if r.status_code == 200:
        return r.json()
    else:
        raise ConnectionError


def download(output_dir, item):
    if 'zip' in item['binaryNames']:
        url = item['binaries']['zip']['url']
    else:
        return False
    return wget.download(url, out=output_dir)


def filter_files(unzipped_dir):
    files = []
    for file in os.listdir(unzipped_dir):
        filename, ext = os.path.splitext(file)
        if ext.lower() == '.dae':
            new_file = f'{unzipped_dir.split("/")[-1]}.dae'
            os.rename(f'{unzipped_dir}/{file}', f'{unzipped_dir}/{new_file}')
            files.append(new_file)
    return files


def is_model(cadid):
    return not db.read(f"SELECT * from cad_file WHERE source=2 and source_id='{cadid}'").empty


def insert_search_log(keyword, total):
    return db.insert('search_log', **{'keyword': keyword, 'website': '3DW', 'total': total})


def insert_dw_file(id, name, image, filepath, keyword):
    if not os.path.isfile(filepath):
        raise FileNotFoundError

    filepath = filter_escape_char(filepath)
    payload = {
        'name': name,
        'source_id': id,
        'file': filepath,
        'web_image': image,
        'source': 3,
        'image': filepath.replace('/3DW/', '/image/3DW/').replace('.obj', '.png'),
        'label': keyword,
        'file_size': os.path.getsize(filepath)
    }
    return db.insert('cad_file', ignore=True, **payload)


def update_thumbnail():
    db.read('select * from ')


def run(keyword, title_matching=False):
    per_search = 100
    init_results = search(keyword, per_search, offset=0)
    total = init_results['total']
    total_search = total // per_search
    insert_search_log(keyword, total)
    print(f'{total} models found')

    output_dir = f'{dw_path}/{keyword}'
    make_dir(output_dir)

    for i in range(total_search + 1):
        results = search(keyword, per_search, offset=i * per_search)
        for item in tqdm(results['entries']):
            try:
                id = item['id']
                name = filter_escape_char(item['title'])

                if is_model(id):
                    continue

                if title_matching and keyword not in item['title'].lower():
                    continue

                zip_file = download(output_dir, item)
                if not zip_file:
                    continue

                unzipped_dir = unzip_file(zip_file)
                files = filter_files(unzipped_dir)
                for file in files:
                    moved_file = move_file(join(unzipped_dir, file), output_dir)
                    obj_file = convert_to_obj(moved_file)

                    # if 'bot_smontage' in item['binaryNames']:
                    #     image = item['binaries']['bot_smontage']['contentUrl']
                    # else:
                    image = item['binaries']['bot_lt']['contentUrl']

                    insert_dw_file(id, name, image, obj_file, keyword)

                shutil.rmtree(unzipped_dir)

            except Exception as e:
                logging.error(f'[{keyword}]:{e}')

    clean_dir(output_dir)
    create_image(output_dir)
