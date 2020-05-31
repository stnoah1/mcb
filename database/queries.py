select_keywords = '''
    SELECT id, name
    FROM keyword
    WHERE use=true
    ORDER by name;
'''
select_taxonomy = '''
    SELECT id, name
    FROM keyword
    WHERE use = True and parent=0
    ORDER BY name;
'''
select_images = '''
    SELECT id,
        name,
        SPLIT_PART(file, '/', 6) as original_label
    FROM cad_file
    WHERE label = {label} and file like '%%.obj' {cad_type}
    order by original_label, file_size, name;
'''

check_trace_part_data = '''
    SELECT *
    FROM cad_file
    where source = 4 and file like '%%{file}%%';
'''
select_category = '''
    SELECT id, name
    FROM keyword
    WHERE use = True and parent={parent}
    ORDER BY name;
'''

update_label = '''
    UPDATE cad_file
    SET label='{label}'
    WHERE id='{id}';
'''

select_object_by_id = '''
    SELECT *
    FROM cad_file
    WHERE id='{id}';
'''

stats = '''
    SELECT B.name as Category, A.SubCategory, A.ME444, A.Data_Warehouse, A.grabCAD, A.TOTAL
    FROM (SELECT CASE WHEN keyword.parent = 0 THEN keyword.id ELSE keyword.parent END as Category,
                 keyword.name                                                         as SubCategory,
                 SUM(CASE WHEN source = 1 THEN 1 ELSE 0 END)                          as ME444,
                 SUM(CASE WHEN source = 2 THEN 1 ELSE 0 END)                          as Data_Warehouse,
                 SUM(CASE WHEN source = 3 THEN 1 ELSE 0 END)                          as grabCAD,
                 COUNT(*)                                                             as TOTAL
          FROM cad_file
          LEFT JOIN keyword
          ON cad_file.label = keyword.id
          WHERE file like '%%.obj'
            and label >= 0
            and use = true
          GROUP BY keyword.id
          ORDER BY Category ASC
         ) AS A
    LEFT JOIN keyword B
    ON A.Category = B.id
    ORDER BY A.Category
'''

select_unlabeled = '''
    SELECT id,
           name,
           SPLIT_PART(file, '/', 6) as original_label
    FROM cad_file
    WHERE label = ''
    ORDER BY name;
'''

select_dataset = '''
    SELECT A.id,
           A.name,
           A.file,
           CASE WHEN A.parent = 0 THEN Null ELSE A.subcategory END as subcategory,
           CASE WHEN A.parent = 0 THEN A.subcategory ELSE B.name END as category
    FROM (SELECT cad_file.id, cad_file.name, file, parent, keyword.name as subcategory
          FROM cad_file
          LEFT JOIN keyword
              ON cad_file.label = keyword.id
          WHERE file like '%%.obj'
            and label >= 0
            and use = true
            and keyword.name <> 'miscellaneous'
         ) A
    LEFT JOIN keyword B
        ON A.parent = B.id
'''
