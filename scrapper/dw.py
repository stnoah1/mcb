import requests
import wget
from tqdm import tqdm

import db
from utils import make_dir
from config import dw_path
from scrapper.base import filter_escape_char

url = 'https://3dwarehouse.sketchup.com/warehouse/v1.0/entities'


def search(keyword, per_search, offset=0):
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


def download(keyword, item):
    if keyword not in item['title'].lower():
        return False

    if 's18' in item['binaryNames']:
        url = item['binaries']['s18']['url']
    elif 's17' in item['binaryNames']:
        url = item['binaries']['s17']['url']
    elif 's16' in item['binaryNames']:
        url = item['binaries']['s16']['url']
    else:
        return False

    output_dir = f'{dw_path}/{keyword}'
    make_dir(output_dir)

    return wget.download(url, out=output_dir)


def is_model(cadid):
    return not db.query(f"SELECT * from dw_files WHERE id='{cadid}'").empty


def insert_search_log(keyword, total):
    return db.insert('search_log', **{'keyword': keyword, 'website': '3DW', 'total': total})


def insert_model(id, name, image, path):
    return db.insert('dw_files', ignore=True, **{'id': id, 'name': name, 'image': image, 'path': path})


def run(keyword):
    per_search = 100
    init_results = search(keyword, per_search, offset=0)
    total = init_results['total']
    total_search = total // per_search
    insert_search_log(keyword, total)
    print(f'{total} models found')
    for i in range(total_search + 1):
        results = search(keyword, per_search, offset=i * per_search)
        for item in tqdm(results['entries']):
            id = item['id']
            name = item['title']
            name = filter_escape_char(name)

            if is_model(id):
                continue

            path = download(keyword, item)
            if not path:
                continue

            if 'bot_smontage' in item['binaryNames']:
                image = item['binaries']['bot_smontage']['contentUrl']
            else:
                image = item['binaries']['bot_lt']['contentUrl']

            insert_model(id, name, image, path)
