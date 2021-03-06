import json
import os
from pprint import pprint
from zipfile import ZipFile

import pandas as pd
from flask import Flask, request, render_template, send_from_directory, after_this_request

from database import queries
from database.agent import read, query

app = Flask(__name__)


def get_cad_imgs(label, cad_type):
    return read(queries.select_images.format(label=label, cad_type=cad_type))


def get_unlabeled_imgs():
    return read(queries.select_unlabeled)


def get_category():
    return read(queries.select_category.format(parent=0))


def get_dataset():
    return read(queries.select_taxonomy)


def get_subcategory(parent):
    return read(queries.select_category.format(parent=parent))


def update_item(ids, label):
    for id in ids:
        query(queries.update_label.format(label=label, id=id))


def get_miscellaneous():
    return read("SELECT * FROM keyword WHERE parent=214")


@app.route("/filter", methods=["POST"])
def remove_item():
    payload = json.loads(request.data)
    pprint(payload)
    if payload['ids']:
        update_item(payload['ids'], payload['label'])
    return "success"


@app.route('/obj/<id>')
def get_obj(id):
    obj_path = read(queries.select_object_by_id.format(id=id))['file'][0]
    return send_from_directory(os.path.dirname(obj_path), os.path.basename(obj_path))


@app.route('/zip/<id>')
def get_zip(id):
    obj_path = read(queries.select_object_by_id.format(id=id))['file'][0]
    zip_path = obj_path.replace('.obj', 'zip')

    with ZipFile(zip_path, 'w') as zip:
        zip.write(obj_path)

    @after_this_request
    def remove_zipfile(response):
        try:
            os.remove(zip_path)
        except Exception as e:
            print(e)
        return response

    return send_from_directory(os.path.dirname(zip_path), os.path.basename(zip_path))


@app.route("/subcategory", methods=["GET"])
def subcategory():
    parent = request.args.get('category', '')
    return get_subcategory(parent).to_json(orient='records')


@app.route('/image/<id>')
def get_img(id):
    img_path = read(queries.select_object_by_id.format(id=id))['image'][0]
    return send_from_directory(os.path.dirname(img_path), os.path.basename(img_path))


@app.route("/OBJViewer")
def obj_viewer():
    return render_template(f'OBJViewer.html')


@app.route("/viewer")
def viewer():
    return render_template(f'viewer.html')


@app.route("/annotator", methods=["GET"])
def annotator():
    cad_type = request.args.get('cad', '')
    if cad_type == '0':
        condition = ''
    else:
        condition = f'and source = {cad_type}'
    keyword = request.args.get('keyword', '')
    img_info = get_cad_imgs(keyword, condition)
    print(f'{len(img_info)} was found!!')
    return render_template('gallery.html', img_info=img_info[:500], keywords=get_miscellaneous(),
                           labels=get_category(), num_file=str(len(img_info)))


@app.route("/taxonomy_viewer", methods=["GET"])
def taxnomy_viewer():
    category = request.args.get('category', -1)
    subcategory = request.args.get('subcategory', -1)
    if subcategory == '0':
        keyword = category
    elif subcategory == -1:
        keyword = -2
    else:
        keyword = subcategory


    img_info = get_cad_imgs(keyword, '')

    print(f'{len(img_info)} models found')
    return render_template('taxonomy_viewer.html', img_info=img_info.sample(frac=1), keywords=get_miscellaneous(),
                           labels=get_dataset(), num_file=str(len(img_info)))

@app.route("/")
def index():
    return render_template('taxonomy_viewer.html', img_info=pd.DataFrame(), keywords=get_miscellaneous(),
                           labels=get_category(), num_file='')


@app.route('/stats', methods=("POST", "GET"))
def stat():
    df = read(queries.stats)
    df.columns = [column.upper() for column in df.columns]
    df = df[df.CATEGORY != 'miscellaneous']
    df['CATEGORY'] = [item.upper() for item in df['CATEGORY']]
    df['SUBCATEGORY'] = [item.capitalize() for item in df['SUBCATEGORY']]
    df = df.pivot_table(index=['CATEGORY', 'SUBCATEGORY'],
                        margins=True,
                        margins_name='======= TOTAL =======',  # defaults to 'All'
                        aggfunc=sum)
    return render_template('stats.html', tables=[df.to_html(table_id='stats', classes='data', header="true")])
