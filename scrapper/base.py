import os
import shutil

from config import assimp_path
from database.agent import read


def filter_escape_char(char):
    return char.replace("\'", "\'\'")


def unzip_file(zip_file, output_dir=None):
    if not output_dir:
        output_dir = zip_file.replace('.zip', '')

    # import zipfile
    # zip_ref = zipfile.ZipFile(zip_file, 'r')
    # zip_ref.extractall()
    # zip_ref.close()
    os.system(f'unzip -o "{zip_file}" -d "{output_dir}"')
    os.remove(zip_file)
    return output_dir


def move_file(file, dst_dir, overwrite=True):
    basename = os.path.basename(file)
    head, tail = os.path.splitext(basename)
    dst_file = os.path.join(dst_dir, basename)

    if overwrite:
        count = 0
        while os.path.exists(dst_file):
            count += 1
            dst_file = os.path.join(dst_dir, '%s_%d%s' % (head, count, tail))

    shutil.move(file, dst_file)
    return dst_file


def convert_to_obj(file):
    basename = os.path.basename(file)
    filename, ext = os.path.splitext(basename)
    if ext.lower() in ['.stl', '.dae']:
        obj_file = file.replace(ext, '.obj')
        os.system(f'{assimp_path} export "{file}" "{obj_file}"')
        os.remove(file)

        mtl_file = file.replace(ext, '.mtl')
        if os.path.exists(mtl_file):
            os.remove(mtl_file)
        return obj_file
    else:
        return file


def stp_to_stl(file):
    basename = os.path.basename(file)
    filename, ext = os.path.splitext(basename)
    if ext.lower().endswith('.stp'):
        import gmsh

        stl_file = file.replace(ext, '.stl')
        gmsh.initialize()
        gmsh.open(file)
        gmsh.write(stl_file)
        gmsh.clear()

        os.remove(file)
        return stl_file
    else:
        raise TypeError


def stp_to_obj(file):
    stl_file = stp_to_stl(file)
    print(stl_file)
    return convert_to_obj(stl_file)


def get_keyword_id(keyword):
    return read(f"SELECT * from keyword where name = '{keyword}'")['id'][0]


if __name__ == "__main__":
    print('test')
