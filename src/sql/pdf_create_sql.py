import requests
from .secret_keys_SQL import NOTION_TOKEN, notion_headers

##data acquisition
print(NOTION_TOKEN)

def shortened_ids(link):
    last_hyphen = link.rfind("-")
    last_question = link.rfind("?")

    if last_question == -1:
        page_id_trunc = link[last_hyphen + 1:]
    else:
        page_id_trunc = link[last_hyphen + 1:last_question]

    #print(f"Extracted Page ID from Link: {link}")

    return page_id_trunc

def fetch_block_children(block_id):
    try:
        url = f"https://api.notion.com/v1/blocks/{block_id}/children"
        response = requests.get(url, headers=notion_headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching block children for block ID {block_id}: {e}")
        return {"results": []}
    

def rich_text_to_html(rich_text):
    html_content = ""
    for text in rich_text:
        if text['type'] == 'text':
            if 'link' in text['text'] and text['text']['link']:
                url = text['text']['link']['url']
                html_content += f'<a href="{url}">{text["text"]["content"]}</a>'
            else:
                html_content += text['text']['content']
    return html_content


    
def pdf_create_main(dict_list):
    useful_columns = []
    for column in dict_list:
        
        
        
        #link
        if "g_link" in column:
            link = column["g_link"]
            global notion_id
            notion_id = shortened_ids(link)
        else:
            print("no link, error")
            

        #name
        if "g_name" in column:
            name = column["g_name"]
        else:
            name = column["g_name"]
        print("pre cat")


        #category
        if "g_category" in column:
            category = column["g_category"]
        else:
            category = "NaN"


        print("pre edit")
        #editor

        


        if "edit" in column:
            edit = column["edit"]
        else:
            edit = "NaN"
        
        if "qa" in column:
            edit = qa["qa"]
        else:
            qa = "NaN"


        print("heee")

        useful_columns.append(
            {
        "link": link,
        "notion_id": notion_id,
        "name": name,
        "category":category,
        "edit": edit,
        "qa": qa
        }
        )


    #print(useful_columns)


    return useful_columns
    
    

