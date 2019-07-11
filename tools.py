import os
from shutil import copyfile

import numpy as np
import pandas as pd
from sklearn.utils import shuffle
from tqdm import tqdm

from config import dw_path, grabcad_path
from database import queries
from database.agent import read
from utils.mat_api import MatlabAPI
from utils.utils import make_dir


def get_keywords():
    return read(queries.select_keywords)


def purify(string):
    return string.lower().replace(' ', '_').replace('-', '_').replace('/', '_or_')


def make_dataset_1(path):
    data = read(queries.select_dataset)
    with open(os.path.join(path, 'label.csv'), 'w') as f:
        for idx, item in tqdm(data.iterrows()):
            filename = "%08d" % item['id'] + '.obj'
            if os.path.isfile(item['file']):
                copyfile(item['file'], os.path.join(path, filename))
                item['subcategory'] = item['subcategory'] if item['category'] else 'null'
                f.write(','.join([filename, 'null', purify(item['category']), purify(item['subcategory'])]) + '\n')
            else:
                print(filename, item['id'])


def make_dataset_2(path, categories=None):
    data = read(queries.select_dataset)
    if categories:
        data = data[data['category'].isin(categories)]

    eval_portion = 0.1
    test_portion = 0.2

    data['subcategory'] = [item if item else data.loc[idx, 'category'] for idx, item in enumerate(data['subcategory'])]
    subcategories = list(set(data['subcategory'].tolist()))

    f_train = open(os.path.join(path, 'train.csv'), 'w')
    f_test = open(os.path.join(path, 'test.csv'), 'w')
    f_eval = open(os.path.join(path, 'eval.csv'), 'w')

    for subcategory in tqdm(subcategories):
        if subcategory == 'None':
            continue

        subcat_set = data[data['subcategory'] == subcategory]
        subcat_set = shuffle(subcat_set)

        num_subcat_set = len(subcat_set)
        num_subset_eval_set = int(num_subcat_set * eval_portion)
        num_subset_test_set = int(num_subcat_set * test_portion)

        if num_subset_eval_set < 3:
            continue

        for idx, (_, item) in enumerate(subcat_set.iterrows()):
            filename = "%08d" % item['id'] + '.obj'
            item['subcategory'] = purify(item['subcategory'])
            item['category'] = purify(item['category'])

            if idx < num_subset_eval_set:
                data_type = 'eval'
                file = f_eval
            elif idx < num_subset_eval_set + num_subset_test_set:
                data_type = 'test'
                file = f_test
            else:
                data_type = 'train'
                file = f_train

            dst_path = os.path.join(path, data_type, item['subcategory'])
            make_dir(dst_path)
            obj_file = os.path.join(dst_path, filename)
            copyfile(item['file'], obj_file)

            normalized_mesh = normalize_mesh(obj_file)

            with open(obj_file, 'w') as f:
                f.write(normalized_mesh)

            file.write(','.join([filename, 'null', item['category'], item['subcategory']]) + '\n')

    f_test.close()
    f_train.close()
    f_eval.close()


def create_all_image():
    for cad_dir in [dw_path, grabcad_path]:
        for directory in os.listdir(cad_dir):
            create_image(os.path.join(cad_dir, directory))


def create_image(directory):
    matlab_api = MatlabAPI()

    if os.path.isdir(directory):
        matlab_api.make_image(directory)

    matlab_api.close()


def normalize_vertices(pc):
    centroid = np.mean(pc, axis=0)
    pc = pc - centroid
    m = np.max(np.sqrt(np.sum(pc ** 2, axis=1)))
    pc = pc / m
    return pc


def normalize_mesh(mesh_file, output_type='obj'):
    import trimesh

    mesh = trimesh.load(mesh_file)
    mesh.vertices = normalize_vertices(mesh.vertices)
    return mesh.export(file_type=output_type)


def evaluation(source_dir):
    data_type = 'train'
    data_list = pd.read_csv(f'{source_dir}/{data_type}.csv', header=None)
    train_file_list = []
    for idx, item in data_list.iterrows():
        file_path = os.path.join(source_dir, data_type, item[3], item[0])

        if not os.path.exists(file_path):
            print(file_path + 'not exists')
        else:
            train_file_list.append(file_path)

    data_type = 'test'
    data_list = pd.read_csv(f'{source_dir}/{data_type}.csv', header=None)
    test_file_list = []
    for idx, item in data_list.iterrows():
        file_path = f'{source_dir}/{data_type}/{item[3]}/{item[0]}'
        # print(file_path)
        if not os.path.exists(file_path):
            print(file_path + 'not exists')
        else:
            test_file_list.append(file_path)

    for test_file in test_file_list:
        if test_file in train_file_list:
            print(test_file)


if __name__ == "__main__":
    make_dataset_2("/mnt/data/ENGR_data/dataset")
