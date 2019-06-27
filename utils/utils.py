import os
import shutil
from shutil import copyfile

from tqdm import tqdm

from config import dw_path, grabcad_path
from database import queries
from database.agent import read
from utils.mat_api import MatlabAPI


def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def clean_all_dir(directory):
    for subdir in os.listdir(directory):
        keyword_path = os.path.join(directory, subdir)
        clean_dir(keyword_path)


def clean_dir(directory):
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)


def get_keywords():
    return read(queries.select_keywords)


def make_dataset(path):
    data = read(queries.select_dataset)
    with open(os.path.join(path, 'label.csv'), 'w') as f:
        for idx, item in tqdm(data.iterrows()):
            filename = "%08d" % item['id'] + '.obj'
            if os.path.isfile(item['file']):
                copyfile(item['file'], os.path.join(path, filename))
                f.write(','.join([
                    filename,
                    'null',
                    item['category'].lower().replace(' ', '_').replace('-', '_').replace('/', '_or_'),
                    (item['subcategory'] if item['subcategory'] else 'null').lower().replace(' ', '_').replace('-', '_').replace('/', '_or_')
                ]) + '\n')
            else:
                print(filename, item['id'])


def create_all_image():
    for cad_dir in [dw_path, grabcad_path]:
        for directory in os.listdir(cad_dir):
            create_image(os.path.join(cad_dir, directory))


def create_image(directory):
    matlab_api = MatlabAPI()

    if os.path.isdir(directory):
        matlab_api.make_image(directory)
