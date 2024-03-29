## Introduction
We introduce a web-based data acquisition and annotation tool for Mechanical Components. We collect models from online 3D CAD repositories To effectively annotate, CAD models are filtered and annotated using with this tools. We define classes by following the field '*Mechanical 290 Systems and Components*' of the [International Classification for Standards (ICS)](https://www.iso.org/publication/PUB100033.html) published by International Organization for Standardization (ISO). You can find more details on our project page ([link](https://mechanical-components.herokuapp.com/)). Download link to [Dataset A](https://app.box.com/s/lwvmxbu8v75g5hd1ulaloszte0l1t1n9) and [Dataset B](https://app.box.com/s/pve9x614z10od4glr5tatgqyuya4b52v).

![overview](overview.png)

## Setup
### 1. Install
* Install Python dependencies
```Bash
pip install -r requirements.txt
```
* Install [ASSIMP](https://github.com/assimp/assimp) for file format conversion.

### 2. Make `config.py`
Create `config.py` following format,
```Python
# data download directory
grabcad_path = 'PATH/TO/GRABCAD_FILES'
dw_path = 'PATH/TO/3DW_FILES'

# web hosting info
host = '127.0.0.1'

# database info
dbhost = '127.0.0.1'
user = 'user'
password = 'password'

# ASSIMP path
assimp_path = 'PATH/TO/ASSIMP'

# TraceParts
api_key = ''
login_id = ''
```

### 3. Create Database
* Create `keyword` table.
```SQL
create table keyword
(
    id      serial      not null
        constraint keyword_pk
            primary key,
    name    varchar(50) not null,
    use     boolean default true,
    parent  integer
        constraint keyword_keyword_id_fk
            references keyword,
    dataset boolean
);

create unique index keyword_id_uindex
    on keyword (id);
```
* Create `cad_file` table.
```SQL
create table cad_file
(
    id        serial  not null
        constraint cad_file_pk_2
            primary key,
    source    integer not null
        constraint cad_file_source_id_fk
            references source,
    name      varchar(300),
    file      varchar(400),
    web_image varchar(400),
    image     varchar(400),
    label     integer,
    timestamp timestamp default now(),
    remark    varchar(500),
    source_id varchar(200),
    file_size integer
);

create unique index cad_file_id_uindex
    on cad_file (id);
```
## Usage
### Run Data collector
We provide mechanical components collector for online large 3D CAD repositories: [TraceParts](https://www.traceparts.com/), [3D WareHouse](https://3dwarehouse.sketchup.com/), and [GrabCAD](https://grabcad.com/). 3D Warehouse and GrabCAD are large online open repository for professional designers, engineers, manufacturers, and students to share CAD models. They provide numerous CAD models with various classes, including mechanical components.  If you want to collect data from TraceParts, you have to request API key through their website [[link](https://info.traceparts.com/developers/request-api-key/)] and put the `api_key` and `login_id` in the `config.py` file.

```Python
python scrapper.py --keywords=path/to/keywords.txt
```
### Run Web-based UI
A dataset managing platform visualizes multi-view images of each engineering part, which gives users a more comprehensive understanding of the mechanical part during filtering and annotating. [[DEMO](http://68.50.194.108/taxonomy_viewer?category=70&subcategory=0)]
```Python
python web_server.py
```

## Citation
```Tex
 @inproceedings{sangpil2020large,
    title={A Large-scale Annotated Mechanical Components Benchmark for Classification and Retrieval Tasks with Deep Neural Networks},
    author={Kim, Sangpil and Chi, Hyung-gun and Hu, Xiao and Huang, Qixing and Ramani, Karthik},
    booktitle={Proceedings of 16th European Conference on Computer Vision (ECCV)},
    year={2020},}
```
