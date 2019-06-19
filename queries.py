select_keywords = '''
    select id, name from keyword order by name;
'''

select_images = '''
    select id, 
        name, 
        SPLIT_PART(file, '/', 6) as original_label
    from cad_file 
    where label = {label} and file like '%%.obj' {cad_type}
    order by file_size, name;
'''

select_annotation_keywords = '''
    select id, name 
    from keyword 
    where use = True
    order by name;
'''


update_label = '''
    update cad_file set label='{label}' where id='{id}';
'''

select_object_by_id = '''
    select * from cad_file where id='{id}';
'''

stats = '''
    SELECT UPPER(label)                                as LABEL,
           SUM(CASE WHEN source = 1 THEN 1 ELSE 0 END) as ME444,
           SUM(CASE WHEN source = 2 THEN 1 ELSE 0 END) as Data_Warehouse,
           SUM(CASE WHEN source = 3 THEN 1 ELSE 0 END) as grabCAD,
           COUNT(*)                                    as TOTAL
    FROM cad_file
    WHERE file like '%%.obj'and label <> ''
    GROUP BY label
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


