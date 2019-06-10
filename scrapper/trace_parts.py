import requests
from anytree import Node, RenderTree
from anytree.dotexport import RenderTreeGraph

from bs4 import BeautifulSoup

trace_parts_url = 'https://www.traceparts.com'


def get_category(save_img=True):
    url = f'{trace_parts_url}/en/search/traceparts-classification-mechanical-components?CatalogPath=TRACEPARTS%3ATP01'
    print(url)
    r = requests.get(url)

    if r.status_code == 200:

        soup = BeautifulSoup(r.text, 'html.parser')
        root = Node('Mechanical components')
        node = root
        prev_level = 1

        for cat in soup.find_all('span', {'class': 'treeview-node-title'}):
            levels = cat.get('title').split('>')
            levels = [c.strip() for c in levels]

            if levels[0] == 'Mechanical components' and len(levels) > 1:
                depth = len(levels) - prev_level
                prev_level = len(levels)
                if depth <= 0:
                    for i in range(abs(depth) + 1):
                        node = node.parent
                node = Node(levels[-1], parent=node)
                # value=label.get('for')
        for pre, fill, node in RenderTree(root):
            print("%s%s" % (pre, node.name))

        if save_img:
            RenderTreeGraph(root).to_picture("tree.png")

    else:
        raise ConnectionError


get_category()
