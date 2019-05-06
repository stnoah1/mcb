import os
from shutil import copy2

from db import query
from utils import make_dir
from pprint import pprint
labeled_dir = 'labeled'


def file_arrange():
    df = query('select file, labels from models')
    for idx, row in df.iterrows():
        for label in row['labels']:
            src = f'data/{row["file"]}'
            tgt_path = f'{labeled_dir}/{label}'
            make_dir(tgt_path)
            try:
                copy2(src, tgt_path)
            except:
                print(src)


def get_stat():
    labels = os.listdir(labeled_dir)
    labels = [label for label in labels if not label.startswith('.')]
    stat = {}
    for label in labels:
        stat[label] = len(os.listdir(f'{labeled_dir}/{label}'))
    pprint(stat)


if __name__ == '__main__':
    # file_arrange()
    get_stat()
