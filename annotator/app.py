import time
from zipfile import ZipFile
import json
import os
from pprint import pprint

import pandas as pd
from flask import Flask, request, render_template, send_from_directory, after_this_request

import queries
from config import data_path
from db import read, query
from utils import get_keywords

app = Flask(__name__)


def get_3dw_img(label, filter):
    return read(queries.select_image_3dw.format(label=label, filter=filter))


def get_grabcad_img(label, filter):
    return read(queries.select_image_3dw.format(label=label, filter=filter))


def filter_data(cad_type, ids, filter):
    table = {
        '3DW': 'dw_files',
        'grabCAD': 'grabcad_files',
    }
    for id in ids:
        query(queries.update_filter.format(table=table[cad_type], filter=filter, id=id))


@app.route("/gallery", methods=["GET"])
def gallery():
    cad_type = request.args.get('cad', '')
    keyword = request.args.get('keyword', '')
    display = request.args.get('display', '')

    if display == 'filtered':
        filter = True
    elif display == 'deleted':
        filter = False
    else:
        raise ValueError

    if cad_type == "grabCAD":
        img_info = get_grabcad_img(keyword, filter)
    elif cad_type == "3DW":
        img_info = get_3dw_img(keyword, filter)
    else:
        raise ValueError

    print(f'{len(img_info)} was found!!')
    return render_template('gallery.html', img_info=img_info, keywords=get_keywords())


@app.route("/")
def index():
    return render_template('gallery.html', img_info=pd.DataFrame(), keywords=get_keywords())


@app.route('/stats', methods=("POST", "GET"))
def stat():
    df = read(queries.stats)
    df.columns = [column.upper() for column in df.columns]
    df['LABEL'] = [label.upper() for label in df['LABEL']]
    df = df.set_index('LABEL')
    df = df.pivot_table(index='LABEL',
                        margins=True,
                        margins_name='=== TOTAL ===',  # defaults to 'All'
                        aggfunc=sum)
    columns = ['DW_OBJ', 'GRABCAD_OBJ', 'PRT', 'SLDPRT', 'FILTERED', 'DELETED']
    return render_template('stats.html', tables=[df[columns].to_html(table_id='stats', classes='data', header="true")])


@app.route("/filter", methods=["POST"])
def remove_item():
    payload = json.loads(request.data)
    pprint(payload)
    if payload['ids']:
        if payload['action'] == 'deleted':
            action = True
        else:
            action = False
        filter_data(payload['cad-type'], payload['ids'], action)
    return "success"


@app.route('/obj/<cad_site>/<category>/<filename>')
def get_obj(cad_site, category, filename):
    obj_path = os.path.join(data_path, cad_site, category)
    return send_from_directory(obj_path, filename)


@app.route('/zip/<cad_site>/<category>/<filename>')
def get_zip(cad_site, category, filename):
    zip_dir = os.path.join(data_path, cad_site, category)
    zip_path = os.path.join(zip_dir, filename)

    with ZipFile(zip_path, 'w') as zip:
        zip.write(zip_path.replace('.zip', '.obj'))

    @after_this_request
    def remove_zipfile(response):
        try:
            os.remove(zip_path)
        except Exception as e:
            print(e)
        return response

    return send_from_directory(zip_dir, filename)


@app.route('/image/<cad_site>/<category>/<filename>')
def get_img(cad_site, category, filename):
    img_path = os.path.join(data_path, 'image', cad_site, category)
    return send_from_directory(img_path, filename)


@app.route("/OBJViewer")
def obj_viewer():
    return render_template(f'OBJViewer.html')


@app.route("/viewer")
def viewer():
    return render_template(f'viewer.html')


@app.route("/annotator")
def annotator():
    return render_template(f'annotator.html', labels=get_keywords())
