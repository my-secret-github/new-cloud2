from interpret_sql import column_name_function


def pdf_ready(input):


    #compile data
    rows = input
    columns = column_name_function()


    dictionary = {}

    dict_list = []
    for row in enumerate(rows):
        x = {}
        i=0
        for column in columns:
            x.update({f'{column}': row[1][i]})
            i+=1

        dict_list.append(x)

    #get important info
    return dict_list


