import logging
from datetime import datetime
import db
from scrapper import grab_cad, dw
from utils import make_dir

make_dir('log')
logging.basicConfig(filename=f'log/{datetime.now().strftime("%y%m%d_%H%M%S")}.log', level=logging.ERROR)


def search(keyword, websites=['grabcad', '3dw']):
    logging.info(f'KEYWORD: {keyword}')

    if 'grabcad' in websites:
        logging.info('graCAD')
        grab_cad.run(keyword=keyword, softwares=['obj', 'stl', 'ptc-creo-parametric', 'solidworks'])

    if '3dw' in websites:
        logging.debug('3DW')
        dw.run(keyword=keyword)


def search_keywords_db():
    keywords = db.read('SELECT * FROM keyword')

    for idx, keyword in keywords.iterrows():
        search(keyword['name'], websites=['3dw'])


if __name__ == "__main__":
    for keyword in ['lock', 'multimeter', 'opener', 'pencil', 'protractor', 'scissors',
                    'sharpie', 'spoon', 'stapler', 'tong', 'tweezer', 'whisk']:
        search(keyword, websites=['3dw'])
