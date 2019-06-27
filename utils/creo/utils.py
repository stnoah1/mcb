import os
from os.path import splitext

import numpy as np
import trimesh
from trimesh import load_mesh
from trimesh.exchange.export import export_off


class FileFormatError(Exception):
    pass


def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def stl2off(stl_file, off_file=None, delete_file=True):
    file_format_check(stl_file, '.stl')
    if off_file is None:
        off_file = stl_file.replace('.stl', '.off')
    mesh = load_mesh(stl_file)
    off_data = export_off(mesh)
    with open(off_file, 'w') as f:
        f.write(off_data)
    if delete_file:
        os.remove(stl_file)
    return off_file


def file_format_check(file, file_format):
    _, file_ext = splitext(file)
    if file_ext.lower() != file_format.lower():
        raise FileFormatError


def save_image(stl_file, output_dir='', angle=np.radians(45.0), direction=None, resolution=None):
    if resolution is None:
        resolution = [640, 480]
    if direction is None:
        direction = [1, 1, 1]
    if output_dir:
        make_dir(output_dir)

    mesh = load_mesh(stl_file)

    base = os.path.basename(stl_file)
    filename, ext = splitext(base)

    scene = mesh.scene()
    scene.set_camera()

    rotate = trimesh.transformations.rotation_matrix(
        angle=angle,
        direction=direction,
        point=scene.centroid)

    trimesh.constants.log.info('Saving image %d', )

    camera_old, _geometry = scene.graph['camera']
    camera_new = np.dot(camera_old, rotate)

    scene.graph['camera'] = camera_new

    try:
        png = scene.save_image(resolution=resolution, visible=True)
        with open(os.path.join(output_dir, filename + '.png'), 'wb') as f:
            f.write(png)
            f.close()
    except BaseException as E:
        print("unable to save image", str(E))
