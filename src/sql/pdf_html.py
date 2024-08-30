from bucket_upload2 import upload_to_bucket, upload_image_to_bucket
from main_sql import bucket_name
import tempfile
from weasyprint import HTML
import os
from pdf_to_drive import upload_to_drive
import requests
from sql.secret_keys_SQL import notion_headers

import os


#css
from pdf_css.pdf_pg_1 import pg_1_style
from pdf_css.pdf_general_style import pdf_general_style
from pdf_css.notion_blocks import notion_block_style

#js progress
from main_sql import update_progress

#boilerplate
from pdf_boilerplate import html_boilerplate_start



def fetch_page_content(notion_id):
    try:
        url = f"https://api.notion.com/v1/blocks/{notion_id}/children"
        response = requests.get(url, headers=notion_headers)
        response.raise_for_status()
        print(f"Fetched content for page ID {notion_id}")
        return response.json()
    except Exception as e:
        print(f"Error fetching page content for page ID {notion_id}: {e}")
        return {"results": []}


def notion_blocks_to_html(blocks):

    html_content = ""
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
    
    def fetch_block_children(block_id):
        try:
            url = f"https://api.notion.com/v1/blocks/{block_id}/children"
            response = requests.get(url, headers=notion_headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching block children for block ID {block_id}: {e}")
            return {"results": []}

    inside_image_container = False

    for i, block in enumerate(blocks):
        block_type = block.get("type", "unsupported")
        if block_type == "paragraph":
            if inside_image_container:
                html_content += "</div>"
                inside_image_container = False
            if block['paragraph']['rich_text']:
                html_content += f"<p>{rich_text_to_html(block['paragraph']['rich_text'])}</p>"
            else:
                html_content += "<p></p>"


        elif block_type in ["heading_1", "heading_2", "heading_3"]:
            if inside_image_container:
                html_content += "</div>"
                inside_image_container = False
            level = block_type[-1]
            rich_text = block[block_type].get('rich_text', [])
            if rich_text:
                html_content += f"<h{level} class='h{level}'>{rich_text_to_html(rich_text)}</h{level}>"        

       
        elif block_type == "image":
            if not inside_image_container:
                html_content += '<div class="image-container">'
                inside_image_container = True

            image_data = block.get("image", {})
            image_url = image_data.get("file", {}).get("url", "")
            if not image_url:
                continue  # Skip this block if no URL is found

            # Upload the image to Google Cloud Storage and get public URL
            
            public_url = upload_image_to_bucket(image_url, bucket_name)

            next_block_type = blocks[i + 1].get("type", "unsupported") if i + 1 < len(blocks) else None
            if next_block_type == "image":
                html_content += f'<img src="{public_url}" alt="Image" class="half">'
            else:
                html_content += f'<img src="{public_url}" alt="Image" class="full">'
                if i + 1 < len(blocks) and blocks[i + 1].get("type", "unsupported") == "paragraph":
                    html_content += '<div class="text">'
                    html_content += f"<p>{rich_text_to_html(blocks[i + 1]['paragraph']['rich_text'])}</p>"
                    html_content += '</div>'



        
        elif block_type == "video":
            if inside_image_container:
                html_content += "</div>"
                inside_image_container = False
            video_url = block["video"].get("external", {}).get("url")
            if not video_url:
                video_url = block["video"].get("file", {}).get("url")
            if video_url:
                html_content += f'<p><a href="{video_url}">Watch Video</a></p>'
        
        
        
        elif block_type == "file":
            if inside_image_container:
                html_content += "</div>"
                inside_image_container = False
            file_url = block["file"].get("external", {}).get("url")
            if not file_url:
                file_url = block["file"].get("file", {}).get("url")
            if file_url:
                html_content += f'<p><a href="{file_url}">Download File</a></p>'
        
        
        
        elif block_type in ["column_list", "column", "toggle", "bulleted_list_item", "numbered_list_item"]:
            if inside_image_container:
                html_content += "</div>"
                inside_image_container = False
            if block['has_children']:
                child_blocks = fetch_block_children(block['id'])["results"]
                html_content += notion_blocks_to_html(child_blocks)
        
        
        else:
            print(f"Unsupported block type: {block_type}")
    

    if inside_image_container:
        html_content += "</div>"

    html_content += """
    </body>
    </html>
    """

    return html_content



def generate_page_one(useful_columns, fName, style):
    
    #Import Boilerplate Info

    html_content = html_boilerplate_start(pdf_general_style)

    html_content += f'<h1 class="first_page_title">{fName}\'s Content Guidelines</h1>'

    html_content += f"""
    <div class="intro-page">
        <h2>Hi {fName}, these are your personalized editing guidelines made in our unique <u> {style} editing style</u>.</h2>
        <p> Please make sure that you take the time to read everything attached, as we've spent a lot of time building this, and it is <u>crucial</u> these guides are followed. </p>
    """

    html_content += """</div>"""
    
    #setup first page
    current_category = None
    category = None
    html_content += '<div> <h3 class="category-list"> Categories: </h3>'
    for row in useful_columns:
        category = row['category']
        if category != current_category:
            #print(row)
            html_content += f"""<h2> {category} </h2> """
            current_category = category

    html_content += """
    </div>
    <div class="page-break"> </div>
    """

    page_one = html_content
    return page_one

#main pdf creation:
def create_pdf_from_pages(useful_columns, fName, style):


    #PAGE 1 - intro page is defined here

    all_html_content = generate_page_one(useful_columns, fName, style)

    global pages_created
    pages_created = 1
    
    global total_pages
    total_pages = len(useful_columns)

    progress_data = f"0 / {total_pages}"
    #this creates a page for every page

    for row in useful_columns:
        #adding my page break  <-- improve later

        #defining values
        link = row["link"]
        notion_id = row["notion_id"]
        docName = row["name"]
        category = row["category"]
        edit = row["edit"]
        qa = row["qa"]

        #1. CREATING THE PAGE
            #page container
        all_html_content += f'<div class="page">'


        #2. CREATING THE HEADER
        all_html_content += f"""
        <div class="main_page-header">
        
        <div class="category_title">
        {category} 
        </div> 
        
        <div class="page_number"> 
        Page {pages_created} 
        </div> 
        
        </div> """

        
        #3. SETTING THE TITLE
        all_html_content += f"""
        <div class="document_title">
        {docName} 
        </div>
        """


        #4. NOTION BLOCKS TO HTML  + BUCKET INFO


        blocks_raw = fetch_page_content(notion_id)


        blocks = blocks_raw["results"]

        all_html_content += notion_blocks_to_html(blocks)

        print("passed notion blocks")
        
        #5. closing the page div

        all_html_content += """</div>"""


        #add page break after every page, unless it's the last page <--- not sure why if we previously added one
        if pages_created < total_pages:
            all_html_content += """<div class="page-break"> </div>"""


        #progress update
        progress_data = {'amount': f'{pages_created} / {total_pages}'}
        try:
            response = requests.post('http://localhost:8080/update_progress', json=progress_data)
            response.raise_for_status()
            print(f"Progress update sent: {progress_data['amount']}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send progress update: {e}")


        pages_created += 1

    all_html_content += """
    </body>
    </html>
    """



    print(f"\n \n \n final html content compiled before creating pdf \n \n \n")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", dir="/tmp") as temp_html_file:
        temp_html_file_path = temp_html_file.name
        temp_html_file.write(all_html_content.encode('utf-8'))  # Ensure content is encoded properly

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir="/tmp") as temp_pdf_file:
        temp_pdf_file_path = temp_pdf_file.name
        HTML(string=all_html_content).write_pdf(temp_pdf_file_path)
        print("pdf temp file written")
    



    # Upload the generated PDF to Google Cloud Storage
    with open(temp_pdf_file_path, 'rb') as pdf_file:
        file_content = pdf_file.read()
    file_name = os.path.basename(temp_pdf_file_path)
    upload_to_bucket(file_name, file_content, bucket_name)  # Correctly pass file_name
    print(f"{file_name} written to bucket")


    #status
    progress_data = {'amount': 'drive'}
    try:
        response = requests.post('http://localhost:8080/update_progress', json=progress_data)
        response.raise_for_status()
        print("Final progress update sent: drive%")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send final progress update: {e}")


    # Upload the PDF to Google Drive
    drive_folder_id = '164lbEWocPLZctVs3GXkdqWFF55yGDh5d'  # Your Google Drive folder ID
    id = upload_to_drive(temp_pdf_file_path, f'{style} Guidelines for {fName}.pdf', drive_folder_id)
    print("http")

    # Clean up temporary files
    os.remove(temp_html_file_path)
    os.remove(temp_pdf_file_path)

    #Progress Complete
    progress_data = {'amount': '100'}
    try:
        response = requests.post('http://localhost:8080/update_progress', json=progress_data)
        response.raise_for_status()
        print("Final progress update sent: 100%")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send final progress update: {e}")

    return f"https://drive.google.com/file/d/{id}"