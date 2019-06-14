select_keywords = '''
    select name from keyword order by name;
'''

select_images = '''
    select id, 
        name 
    from cad_file 
    where lower(label) = '{label}' and file like '%%.obj' {cad_type}
    order by file_size, name;
'''

update_filter = '''
    update cad_file set label='' where id='{id}';
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

stats_new = '''

'''