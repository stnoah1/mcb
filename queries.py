select_keywords = '''
    select id, name 
    from keyword 
    WHERE use=true 
    order by name;
'''

select_images = '''
    select id, 
        name, 
        SPLIT_PART(file, '/', 6) as original_label
    from cad_file 
    where label = {label} and file like '%%.obj' {cad_type}
    order by file_size, name;
'''

select_category = '''
    select id, name 
    from keyword 
    where use = True and parent={parent}
    order by name;
'''

update_label = '''
    update cad_file set label='{label}' where id='{id}';
'''

select_object_by_id = '''
    select * from cad_file where id='{id}';
'''

stats = '''
    SELECT keyword.name                                as LABEL,
           SUM(CASE WHEN source = 1 THEN 1 ELSE 0 END) as ME444,
           SUM(CASE WHEN source = 2 THEN 1 ELSE 0 END) as Data_Warehouse,
           SUM(CASE WHEN source = 3 THEN 1 ELSE 0 END) as grabCAD,
           COUNT(*)                                    as TOTAL
    FROM cad_file
    LEFT JOIN keyword
    ON cad_file.label = keyword.id
    WHERE file like '%%.obj'and label > 0 and parent = 0 and use = true
    GROUP BY keyword.name
    ORDER BY total DESC
'''

select_unlabeled = '''
    SELECT id,
           name,
           SPLIT_PART(file, '/', 6) as original_label
    FROM cad_file
    WHERE label = ''
    ORDER BY name;
'''


