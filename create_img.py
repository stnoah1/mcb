import os

from config import dw_path, grabcad_path
from mat_api import MatlabAPI

matlab_api = MatlabAPI()


def create_all_image():
    for cad_dir in [dw_path, grabcad_path]:
        for directory in os.listdir(cad_dir):
            create_image(os.path.join(cad_dir, directory))


def create_image(directory):
    if os.path.isdir(directory):
        matlab_api.make_image(directory)
