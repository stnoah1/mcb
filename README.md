# Introduction
We introduce a web-based data acuisition and annotation tool for Mechanical Components. We collect models from online 3D CAD repositories To effectively annotate, CAD models are filtered and annotated using with this tools. We define classes by following the field ”Mechanical 290 Systems and Components” of the International Classification Standard (ICS).

![overview](overview.png)

## Setup
### 1. Install
1.1 Install Python dependencies
```Bash
pip install -r requirements.txt
```
1.2 Install [ASSIMP](https://github.com/assimp/assimp) for file format conversion.

### 2. Make `config.py`
Create `config.py` following format,
```Python
# data download directory
grabcad_path = 'PATH/TO/GRABCAD_FILES'
dw_path = 'PATH/TO/3DW_FILES'

# web hosting info
host = ''

# database info
dbhost = ''
user = ''
password = ''
password = ''

# ASSIMP path
assimp_path = 'PATH/TO/ASSIMP'
```


### 3. Create Database

## Usage
### Run Data collector
We provide mechanical components collector for online large 3D CAD repositories: [TraceParts](https://www.traceparts.com/), [3D WareHouse](https://3dwarehouse.sketchup.com/), and [GrabCAD](https://grabcad.com/). 3D Warehouse and GrabCAD are large online open repository for professional designers, engineers, manufacturers, and students to share CAD models. They provide numerous CAD models with various classes, including mechanical components.
```Python
python scrapper.py --keywords=path/to/keywords.txt
```
### Run Web-based UI
A dataset managing platform visualizes multi-view images of each engineering part, which gives users a more comprehensive understanding of the mechanical part during filtering and annotating. [[DEMO](http://68.50.194.108/taxonomy_viewer?category=70&subcategory=0)]
```Python
python web_server.py
```

## Citation
