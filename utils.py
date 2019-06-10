import os
import shutil

from config import grabcad_path


def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def clean_dir(directory):
    for subdir in os.listdir(directory):
        keyword_path = os.path.join(directory, subdir)
        for item in os.listdir(keyword_path):
            item_path = os.path.join(keyword_path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
