import logging
from datetime import datetime
import db
from scrapper import grab_cad, dw

keywords = db.query('SELECT * FROM keyword')
logging.basicConfig(filename=f'log/{datetime.now().strftime("%y%m%d_%H%M%S")}.log', level=logging.DEBUG)

for idx, keyword in keywords.iterrows():
    try:
        grab_cad.run(keyword=keyword['name'], softwares=['obj', 'stl', 'ptc-creo-parametric', 'solidworks'])
    except Exception as e:
        logging.warning(f'[{keyword}]:{e}')

    try:
        dw.run(keyword=keyword['name'])
    except Exception as e:
        logging.warning(f'[{keyword}]:{e}')
        continue
