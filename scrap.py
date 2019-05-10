import logging
from datetime import datetime
import db
from scrapper import grab_cad, dw

logging.basicConfig(filename=f'log/{datetime.now().strftime("%y%m%d_%H%M%S")}.log', level=logging.ERROR)


def search(keyword, websites=['grabcad', '3dw']):
    logging.info(f'KEYWORD: {keyword}')

    if 'grabcad' in websites:
        logging.info('graCAD')
        try:
            grab_cad.run(keyword=keyword, softwares=['obj', 'stl', 'ptc-creo-parametric', 'solidworks'])
        except Exception as e:
            logging.error(f'[{keyword}]:{e}')

    if '3dw' in websites:

        logging.debug('3DW')
        try:
            dw.run(keyword=keyword)
        except Exception as e:
            logging.error(f'[{keyword}]:{e}')


def search_keywords_db():
    keywords = db.query('SELECT * FROM keyword')

    for idx, keyword in keywords.iterrows():
        search(keyword['name'], websites=['3dw'])


search('latch')
