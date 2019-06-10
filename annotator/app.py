import json
from pprint import pprint

import pandas as pd
from flask import Flask, request, render_template

from db import read, query

app = Flask(__name__)


def get_3dw_img_info(label):
    return read(f'''
        select A.id, A.image, A.name from 
            (select id, image, name, split_part(path, '/', 5) as label, filter
            from dw_files) as A
        where A.label='{label}' and A.filter=True order by A.name;
    ''')


def get_grabcad_img_info(label):
    return read(f'''
        select A.id, A.image, A.name from
            (SELECT gm.id, name, image, split_part(file, '/', 5) as label, filter from grabcad_models as gm
            right join (select cadid, max(file) as file from grabcad_files group by cadid) gf on gm.id = gf.cadid
            ) as A
        where A.label='{label}' and A.filter=True order by A.name;
    ''')


def filter_data(cad_type, ids):
    table = {
        '3DW': 'dw_files',
        'grabCAD': 'grabcad_models',
    }
    for id in ids:
        query(f'''update {table[cad_type]} set filter=FALSE where id='{id}';''')


def get_keywords():
    return read(f'''select name from keyword order by name;''')['name'].tolist()


@app.route("/gallery", methods=["GET"])
def gallery():
    cad_type = request.args.get('cad', '')
    keyword = request.args.get('keyword', '')

    if cad_type == "grabCAD":
        img_info = get_grabcad_img_info(keyword)
    elif cad_type == "3DW":
        img_info = get_3dw_img_info(keyword)
    else:
        raise ValueError

    print(f'{len(img_info)} was found!!')
    return render_template('gallery.html', img_info=img_info, keywords=get_keywords())


@app.route("/")
def index():
    return render_template('gallery.html', img_info=pd.DataFrame(), keywords=get_keywords())


@app.route('/stats', methods=("POST", "GET"))
def stat():
    df = read(
        """
        select dw.label, dw.dw_obj, obj, prt, sldprt, dw_obj + obj + prt + sldprt as total from
        (
            select label, count(*) as dw_obj
            from (
                     select split_part(path, '/', 5) as label
                     from dw_files
                     where filter = True
                 ) as A
            group by label
        ) as dw
        JOIN
        (
            select label,
                   SUM(CASE WHEN LOWER(file) like '%%.obj' THEN 1 ELSE 0 END)    as obj,
                   SUM(CASE WHEN LOWER(file) like '%%.prt' THEN 1 ELSE 0 END)    as prt,
                   SUM(CASE WHEN LOWER(file) like '%%.sldprt' THEN 1 ELSE 0 END) as sldprt
            from (
                     SELECT file, split_part(file, '/', 5) as label
                     from grabcad_models as gm
                              right join grabcad_files as gf
                                         on gm.id = gf.cadid
                     where gm.filter = True
                 ) as A
            group by label
        ) as grabcad
        on dw.label = grabcad.label;
        """
    )
    df.columns = [column.upper() for column in df.columns]
    df['LABEL'] = [label.upper() for label in df['LABEL']]
    df = df.set_index('LABEL')
    df = df.pivot_table(index='LABEL',
                        margins=True,
                        margins_name='=== TOTAL ===',  # defaults to 'All'
                        aggfunc=sum)
    return render_template('stats.html', tables=[df.to_html(table_id='stats', classes='data', header="true")])


@app.route("/filter", methods=["POST"])
def remove_item():
    data = json.loads(request.data)
    pprint(data)
    if data['ids']:
        filter_data(data['cad-type'], data['ids'])
    return "success"

