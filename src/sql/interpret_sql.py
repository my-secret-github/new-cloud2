

def interpret_headers(biglist):
    list = biglist

    global column_names

    column_names = [col[0] for col in list]

    print(column_names)

    html_rows = "<th>Generate PDF? </th>"
    for column in column_names:
        html_rows += f'<th>{column}</th>'

    return html_rows


def column_name_function():
    return column_names

def interpret_rows(biglist):
    rows = biglist

    print("hello")
    html_rows = ""
    for row in rows:
        html_rows += f'<tr class="standard_row">'
        id = row[0]
        html_rows += f'<td><input type="checkbox" id="guide_id_{id}"></td>'

        for item in row:
            if isinstance(item,str) and item.startswith("https://"):
                html_rows += f'''<td class="link">
                <a href="{item}" target="_blank">
                <button class="link_button">Open</button> 
                </a>
                </td>'''
            else:
                html_rows += f'<td>{item}</td>'
        html_rows += '</tr>'

    return html_rows

