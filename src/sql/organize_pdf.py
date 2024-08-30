from from_sql import input_query

def json_to_py(ids):
    #print(f'you printed {ids}')

    sql_data = ""
    for id in ids:
        id = id.lstrip("guide_id_")
        sql_data += f"{id}, "

    sql_data = sql_data.rstrip(" ,")
    

    sql_query = f"select * from guidelines where g_id in ({sql_data})"

    
    selected_guidelines = input_query(sql_query)


    return selected_guidelines

