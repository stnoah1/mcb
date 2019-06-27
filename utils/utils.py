import os
import shutil


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
