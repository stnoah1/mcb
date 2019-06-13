import logging
from datetime import datetime
import db
from scrapper import grab_cad, dw
from utils import make_dir, get_keywords

make_dir('log')
logging.basicConfig(filename=f'log/{datetime.now().strftime("%y%m%d_%H%M%S")}.log', level=logging.ERROR)


def search(keyword, websites=None):
    if websites is None:
        websites = ['grabcad', '3dw']

    keyword = keyword.lower()

    logging.info(f'KEYWORD: {keyword}')

    if keyword not in get_keywords():
        db.insert('keyword', ignore=True, **{'name': keyword})

    if 'grabcad' in websites:
        logging.info('grabCAD')
        grab_cad.run(keyword=keyword, softwares=['obj', 'stl', 'ptc-creo-parametric', 'solidworks'])

    if '3dw' in websites:
        logging.debug('3DW')
        dw.run(keyword=keyword)


def search_keywords_db():
    keywords = get_keywords()

    for idx, keyword in keywords.iterrows():
        search(keyword['name'], websites=['3dw'])


if __name__ == "__main__":
    for keyword in ['stud', 'anchor', 'insert', 'plug', 'brake', 'clutch', 'coupling', 'actuator', 'ball', 'slide',
                    'stock', 'shaft', 'sleeve', 'castor', 'handle', 'gasket', 'piston', 'wiper', 'damper']:
        search(keyword, websites=['3dw', 'grabcad'])
