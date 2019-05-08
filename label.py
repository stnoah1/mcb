import glob
import os
from shutil import copy2

import db
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


def label_ME444():
    label_mapping = db.query('SELECT id, name FROM labels')
    for cls in os.listdir(labeled_dir):
        for obj_file in glob.glob(f'{labeled_dir}/{cls}/*.obj'):
            basename = os.path.basename(obj_file)
            filename, extention = os.path.splitext(basename)
            label = cls.split(';')[-1].replace('-', ' ')
            label_id = label_mapping.loc[label_mapping.name == label].id.to_list()[0]
            try:
                db.insert('engr_parts', ignore=True, **{'file': filename, 'label': label_id})
            except:
                print(label)


def get_stat_from_dir():
    labels = os.listdir(labeled_dir)
    labels = [label for label in labels if not label.startswith('.')]
    stat = {}
    for label in labels:
        stat[label] = len(os.listdir(f'{labeled_dir}/{label}'))
    pprint(stat)


def get_stat():
    return db.query(
        '''
        SELECT * from
           (SELECT b.name, count(*) as me444
           FROM engr_parts as a
           LEFT JOIN labels as b
           ON a.label = b.id
           GROUP BY b.name) as me444
         FULL OUTER JOIN
           (SELECT split_part(file, '/', 5) as name, count(*) as scrapped
           FROM grabcad_files
           GROUP BY split_part(file, '/', 5)) as scrapped
         ON lower(me444.name) = scrapped.name    
        '''
    )


if __name__ == '__main__':
    # file_arrange()
    # get_stat()
    label_ME444()
