import logging
from datetime import datetime
from database import agent
from scrapper.grab_cad import run as grabCAD_run
from scrapper.dw import run as DW_run
from scrapper.trace_parts import run as traceParts_run
from utils.utils import make_dir
from tools import get_keywords

make_dir('log')
logging.basicConfig(filename=f'log/{datetime.now().strftime("%y%m%d_%H%M%S")}.log', level=logging.ERROR)


def search(keyword, websites=None):
    if websites is None:
        websites = ['grabcad', '3dw']

    keyword = keyword.lower()

    logging.info(f'KEYWORD: {keyword}')

    if keyword not in get_keywords():
        agent.insert('keyword', ignore=True, **{'name': keyword})

    if 'grabcad' in websites:
        logging.info('grabCAD')
        grabCAD_run(keyword=keyword, softwares=['obj', 'stl', 'ptc-creo-parametric', 'solidworks'])

    if '3dw' in websites:
        logging.debug('3DW')
        DW_run(keyword=keyword)


def search_keywords_db():
    keywords = get_keywords()

    for idx, keyword in keywords.iterrows():
        search(keyword['name'], websites=['3dw'])


if __name__ == "__main__":
    # for keyword in ['sleeve']:
    #     search(keyword, websites=['3dw'])
    traceParts_run()
