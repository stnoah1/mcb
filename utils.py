import os
import shutil

import queries
from tqdm import tqdm
from db import read
from shutil import copyfile


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


make_dataset('/mnt/data/ENGR_data/dataset')
