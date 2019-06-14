select_keywords = '''
    select name from keyword order by name;
'''

select_image_3dw = '''
    select id, concat('/image/3DW/{label}/', split_part(replace(path, '.obj', '.png'), '/', 7)) as image, name
    from dw_files
    where split_part(path, '/', 6)='{label}' and filter={filter} order by name;
'''

select_image_grabcad = '''
    select gf.id, concat('/image/grabCAD/{label}/', split_part(replace(file, '.obj', '.png'), '/', 7)) as image, name from grabcad_files as gf
    left join grabcad_models as gm
    on gf.cadid = gm.id
    where split_part(file, '/', 6) = '{label}' and gf.filter={filter} and file like '%%.obj';
'''

select_images = '''
    select id, 
        name 
    from cad_file 
    where lower(label) = '{label}' and file like '%%.obj' {cad_type};
'''

update_filter = '''
    update cad_file set label='' where id='{id}';
'''

select_object_by_id = '''
    select * from cad_file where id='{id}';
'''

stats = '''
    select CASE WHEN grabcad.label is null THEN dw.label ELSE grabcad.label END,
           coalesce(dw_obj, 0) as dw_obj,
           obj - grabcad.deleted as grabcad_obj,
           prt,
           sldprt,
           coalesce(dw_obj, 0) + obj - grabcad.deleted + prt + sldprt as filtered,
           coalesce(dw.deleted, 0) + coalesce(grabcad.deleted, 0) as deleted
    from (
        select label,
              SUM(CASE WHEN filter THEN 1 ELSE 0 END) as dw_obj,
              SUM(CASE WHEN not filter THEN 1 ELSE 0 END) as deleted
        from (
                 select split_part(path, '/', 6) as label, filter
                 from dw_files
             ) as A
        group by label
    ) as dw
    full outer join (
        select label,
               SUM(CASE WHEN LOWER(file) like '%%.obj' THEN 1 ELSE 0 END)    as obj,
               SUM(CASE WHEN LOWER(file) like '%%.prt' THEN 1 ELSE 0 END)    as prt,
               SUM(CASE WHEN LOWER(file) like '%%.sldprt' THEN 1 ELSE 0 END) as sldprt,
               SUM(CASE WHEN not filter THEN 1 ELSE 0 END) as deleted

        from (
                 SELECT file, split_part(file, '/', 6) as label, gf.filter
                 from grabcad_files as gf
                 left join grabcad_models as gm
                 on gm.id = gf.cadid
             ) as A
        group by label
    ) as grabcad
    on dw.label = grabcad.label;
'''

stats_new = '''

'''