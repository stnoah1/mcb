import io
import json
import os
import shutil
import time
import urllib.request
import zipfile
import uuid
from glob import glob
from pprint import pprint

import pandas as pd
import requests
from anytree import Node, RenderTree
from anytree.dotexport import RenderTreeGraph
from bs4 import BeautifulSoup
from tqdm import tqdm

from database import agent, queries
from config import api_key, login_id
from tools import create_image
from scrapper.base import unzip_file, move_file, stp_to_obj
from utils.utils import make_dir
from multiprocessing.pool import ThreadPool

trace_parts_url = 'https://www.traceparts.com'
trace_parts_api_url = 'http://ws.tracepartsonline.net/tpowebservices'
data_path = '/mnt/data/ENGR_data/tracePart'
payload_default = {
    'ApiKey': api_key,
    'Format': 'json',
    'Language': 'en',
}


def extract_filename(response):
    z = zipfile.ZipFile(io.BytesIO(response.content))
    filename = z.filelist[0].filename
    z.extractall()
    return filename


def purify(string):
    return string.replace('/', '_')


def get_url(subpath, payload):
    return f'{trace_parts_api_url}/{subpath}?{"&".join([f"{key}={value}" for key, value in payload.items()])}'


def extract_file(filename, delete=True):
    with open(filename, 'r') as outfile:
        data = json.load(outfile)

    if delete:
        os.remove(filename)

    return data


def print_json(json_file):
    with open(json_file, 'r') as outfile:
        category_list = json.load(outfile)
    pprint(category_list)


def get_exist_files(output_dir):
    return agent.read(queries.check_trace_part_data.format(file=output_dir))['name'].to_list()


def insert_cad_file(filepath, model_name):
    if not os.path.isfile(filepath):
        raise FileNotFoundError

    payload = {
        'name': model_name,
        'file': filepath,
        'source': 4,
        'image': filepath.replace('/tracePart/', '/image/tracePart/').replace('.stp', '.png'),
        'file_size': os.path.getsize(filepath)
    }
    return agent.insert('cad_file', ignore=True, **payload)


def request(url):
    while True:
        r = requests.get(url)
        if r.status_code == 200:
            return r

        elif r.status_code == 503:
            print('Requests limit reached. Wait for 10 minutes')
            time.sleep(10 * 60)

        else:
            print(r.status_code)
            raise ConnectionError


def get_catalogs():
    payload = {**payload_default}
    url = get_url('CatalogsList', payload)
    result = request(url)
    return result.json()['classificationList']


def get_categories(catalog):
    payload = {
        **payload_default,
        'ClassificationID': catalog,
    }

    url = get_url('CategoriesList', payload)
    result = request(url)
    return result.json()['categorieList']


def get_products(catalog, path):
    payload = {
        **payload_default,
        'ClassificationID': catalog,
        'Version': 2,
        'Size': 3000,
        'Path': path
    }

    url = get_url('ProductsList', payload)
    result = request(url)
    return result.json()['productList']


def extract_data(catalog, part_id):
    payload = {
        **payload_default,
        'DataType': 5,
        'Version': 2,
        'CatalogID': catalog,
        'PartId': part_id
    }

    url = get_url('SynchronizationData', payload)
    result = request(url)
    filename = extract_filename(result)
    return extract_file(filename)


def get_cad_url(catalog, part_number):
    payload = {
        **payload_default,
        'UserEmail': login_id,
        'Version': 2,
        'ClassificationID': catalog,
        'PartNumber': part_number,
        'CADFormatID': 19
    }

    url = get_url('DownloadCADPath', payload)
    result = request(url)
    return result.json()['filesPath'][0]['path']


def get_category(save_img=None):
    url = f'{trace_parts_url}/en/search/traceparts-classification-mechanical-components?CatalogPath=TRACEPARTS%3ATP01'
    r = requests.get(url)
    if r.status_code == 200:

        soup = BeautifulSoup(r.text, 'html.parser')
        root = Node('Mechanical components')
        node = root
        prev_level = 1

        for cat in soup.find_all('span', {'class': 'treeview-node-title'}):
            levels = cat.get('title').split('>')
            levels = [c.strip() for c in levels]

            if levels[0] == 'Mechanical components' and len(levels) > 1:
                depth = len(levels) - prev_level
                prev_level = len(levels)
                if depth <= 0:
                    for i in range(abs(depth) + 1):
                        node = node.parent
                node = Node(levels[-1], parent=node)

        for pre, fill, node in RenderTree(root):
            print("%s%s" % (pre, node.name))

        if save_img:
            RenderTreeGraph(root).to_picture(save_img)

    else:
        raise ConnectionError


def download_thread(data):
    print(data['cad_info']['partNumber'])
    cad_url = get_cad_url(data['catalog'], data['cad_info']['partNumber'])
    filename = str(uuid.uuid4()) + '.zip'
    urllib.request.urlretrieve(cad_url, filename=f"{data['output_dir']}/{filename}")
    unzipped_dir = unzip_file(os.path.join(data['output_dir'], filename))
    for file in os.listdir(unzipped_dir):
        if file.endswith('.stp'):
            stp_file = move_file(os.path.join(unzipped_dir, file), data['output_dir'], overwrite=False)
            insert_cad_file(stp_file, data['cad_info']['partNumber'])
    shutil.rmtree(unzipped_dir)


def post_processing(output_dir):
    for stp_file in tqdm(glob(f'{output_dir}/*.stp')):
        obj_file = stp_to_obj(stp_file)
        agent.query(f"update cad_file "
                    f"set file_size={os.path.getsize(obj_file)}, file='{obj_file}' "
                    f"where file='{stp_file}'")

    # create_image(output_dir)


def multi_thread_scrapping(output_dir, catalog, product, num_thread=20):
    make_dir(output_dir)
    exist_files = get_exist_files(output_dir)
    cad_infos = extract_data(catalog, product['partID'])
    unfiltered = pd.DataFrame(cad_infos)
    args = []
    for idx, cad_info in unfiltered.iterrows():
        if cad_info['partNumber'] not in exist_files:
            args.append({'catalog': catalog, 'output_dir': output_dir, 'cad_info': cad_info})

    pool = ThreadPool(num_thread)
    pool.imap_unordered(download_thread, args)
    pool.close()
    pool.join()


def run():
    catalog_list = ['ANSI_INCH', 'ANSI_METRIC', 'DIN']
    category_list = ['Seals', 'Hydraulic fittings', 'Piping components and pipelines in general', 'Flanges', 'Caps',
                     'Elbows', 'Tees', 'Reducers']

    for catalog in catalog_list:
        print(catalog)
        categories = get_categories(catalog)

        for category in categories:
            print('\t', category['title'])
            if category['title'] in category_list:

                products = get_products(catalog, category['path'])

                for product in products:
                    print('\t\t', product['title'])

                    output_dir = f"{data_path}/{catalog}/{purify(category['title'])}/{product['title']}"
                    multi_thread_scrapping(output_dir, catalog, product)
                    post_processing(output_dir)
