import os

from config import dw_path, grabcad_path
from mat_api import MatlabAPI


def make_image(path):
    MatlabAPI().make_image(path)


for cad_dir in [grabcad_path, dw_path]:
    for directory in os.listdir(cad_dir):
        cat_dir = os.path.join(cad_dir, directory)
        if os.path.isdir(cat_dir):
            make_image(cat_dir)
