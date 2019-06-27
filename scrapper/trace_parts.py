import io
import json
import os
import shutil
import time
import urllib.request
import zipfile
import uuid
from pprint import pprint

import requests
from anytree import Node, RenderTree
from anytree.dotexport import RenderTreeGraph
from bs4 import BeautifulSoup

from database import agent, queries
from config import api_key
from scrapper.base import unzip_file, move_file
from utils.utils import make_dir

trace_parts_url = 'https://www.traceparts.com'
trace_parts_api_url = 'http://ws.tracepartsonline.net/tpowebservices'
data_path = '/mnt/data/ENGR_data/tracePart'


def get_category(save_img=True):
    url = f'{trace_parts_url}/en/search/traceparts-classification-mechanical-components?CatalogPath=TRACEPARTS%3ATP01'
    print(url)

    while True:
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
                    # value=label.get('for')
            for pre, fill, node in RenderTree(root):
                print("%s%s" % (pre, node.name))

            if save_img:
                RenderTreeGraph(root).to_picture("tree.png")

            return

        elif r.status_code == 503:
            time.sleep(10 * 60)

        else:
            raise ConnectionError


def get_url(subpath, payload):
    return f'{trace_parts_api_url}/{subpath}?{"&".join([f"{key}={value}" for key, value in payload.items()])}'


def get_zipfile(response):
    z = zipfile.ZipFile(io.BytesIO(response.content))
    filename = z.filelist[0].filename
    z.extractall()
    return filename


def extract_file(filename, delete=True):
    with open(filename, 'r') as outfile:
        data = json.load(outfile)

    if delete:
        os.remove(filename)

    return data


def print_json(json_file):
    with open(json_file, 'r') as outfile:
        category_list = json.load(outfile)
    # category_list = [category for category in category_list if category['catalogId'] != 'ANSI_INCH']
    pprint(category_list)


def get_catalogs():
    payload = {
        'ApiKey': api_key,
        'Format': 'json',
        'Language': 'en',
    }
    url = get_url('CatalogsList', payload)

    while True:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()['classificationList']

        elif r.status_code == 503:
            time.sleep(10 * 60)

        else:
            raise ConnectionError


def insert_cad_file(filepath, model_name):
    # if not os.path.isfile(filepath):
    #     raise FileNotFoundError

    payload = {
        'name': model_name,
        'file': filepath,
        'source': 4,
        'image': filepath.replace('/tracePart/', '/image/tracePart/').replace('.obj', '.png'),
        'file_size': 0  # os.path.getsize(filepath)
    }
    return agent.insert('cad_file', ignore=True, **payload)


def run():
    catalog_list = ['ANSI_INCH', 'ANSI_METRIC', 'DIN']
    for catalog in catalog_list:
        print(catalog)
        categories = get_categories(catalog)

        for category in categories:
            print('\t', category['title'])

            if category['title'].startswith('ANSI') or category['title'].startswith('DIN'):
                continue

            products = get_products(catalog, category['path'])

            for product in products:
                print('\t\t', product['title'])
                cad_infos = extract_data(catalog, product['partID'])

                for cad_info in cad_infos:
                    print(cad_info['partNumber'])

                    if not is_data(cad_info['partNumber']):
                        cad_url = get_cad_url(catalog, cad_info['partNumber'])
                        output_dir = f"{data_path}/{catalog}/{category['title'] if '/' not in category['title'] else category['title'].replace('/', '_')}"
                        make_dir(output_dir)
                        filename = str(uuid.uuid4()) + '.zip'
                        urllib.request.urlretrieve(cad_url, filename=f'{output_dir}/{filename}')
                        unzipped_dir = unzip_file(os.path.join(output_dir, filename))
                        for file in os.listdir(unzipped_dir):
                            if file.endswith('.stp'):
                                moved_file = move_file(os.path.join(unzipped_dir, file), output_dir)
                                # convert file
                                # update file size
                                insert_cad_file(moved_file.replace('.stp', '.obj'), cad_info['partNumber'])
                        shutil.rmtree(unzipped_dir)

                    # update cad_file database
                    # Exception
                # create_image()


def get_categories(catalog):
    payload = {
        'ApiKey': api_key,
        'Format': 'json',
        'Language': 'en',
        'ClassificationID': catalog,
    }

    url = get_url('CategoriesList', payload)
    r = requests.get(url)

    while True:
        if r.status_code == 200:
            return r.json()['categorieList']

        elif r.status_code == 503:
            time.sleep(10 * 60)

        else:
            raise ConnectionError


def get_products(catalog, path):
    payload = {
        'ApiKey': api_key,
        'Format': 'json',
        'Language': 'en',
        'ClassificationID': catalog,
        'Version': 2,
        'Size': 3000,
        'Path': path
    }

    url = get_url('ProductsList', payload)

    while True:
        r = requests.get(url)

        if r.status_code == 200:
            return r.json()['productList']

        else:
            raise ConnectionError


def is_data(dataname):
    return not agent.read(queries.check_trace_part_data.format(name=dataname)).empty


def extract_data(catalog, part_id):
    payload = {
        'ApiKey': api_key,
        'Format': 'json',
        'Language': 'en',
        'DataType': 5,
        'Version': 2,
        'CatalogID': catalog,
        'PartId': part_id
    }

    url = get_url('SynchronizationData', payload)

    while True:
        r = requests.get(url)

        if r.status_code == 200:
            filename = get_zipfile(r)
            return extract_file(filename)

        elif r.status_code == 503:
            time.sleep(10 * 60)

        else:
            raise ConnectionError


def get_cad_url(catalog, part_number):
    payload = {
        'ApiKey': api_key,
        'Format': 'json',
        'UserEmail': 'stnoah1@gmail.com',
        'Language': 'en',
        'Version': 2,
        'ClassificationID': catalog,
        'PartNumber': part_number,
        'CADFormatID': 19
    }

    url = get_url('DownloadCADPath', payload)

    while True:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()['filesPath'][0]['path']

        elif r.status_code == 503:
            time.sleep(10 * 60)

        else:
            raise ConnectionError


run()
# print_json('data/WsCategoriesData_purdue_edu_en.json')
