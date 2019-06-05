from flask import Flask, render_template
from db import query

app = Flask(__name__)


def get_3dw_img_info(label):
    return query(f'''
        select A.image, A.name from 
            (select image, name, split_part(path, '/', 5) as label 
            from dw_files) as A
        where A.label='{label}' order by A.name;
    ''')


def get_grabcad_img_info(label):
    return query(f'''
        select A.image, A.name from
            (SELECT name, image, split_part(file, '/', 5) as label from grabcad_models as gm
            left join grabcad_files gf on gm.id = gf.cadid
            where gf.file notnull) as A
        where A.label='{label}' order by A.name;
    ''')


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/3dw/<string:label>/")
def dw_view(label):
    img_info = get_3dw_img_info(label)
    print(f'{len(img_info)} was found!!')
    return render_template('gallery.html', img_info=img_info)


@app.route("/grabcad/<string:label>/")
def grabcad_view(label):
    img_info = get_grabcad_img_info(label)
    print(f'{len(img_info)} was found!!')
    return render_template('gallery.html', img_info=img_info)


if __name__ == "__main__":
    app.run()
