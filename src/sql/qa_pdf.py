from pdf_boilerplate import html_boilerplate_start
from bucket_upload2 import upload_to_bucket, upload_image_to_bucket
from pdf_to_drive import upload_to_drive
from main_sql import bucket_name



import tempfile
from weasyprint import HTML
import os
import requests





from pdf_css.pdf_general_style import pdf_general_style



def qa_pdf(useful_columns, fName, style):
    
    global all_html_content

#PAGE 1 - intro page is defined here

    all_html_content = html_boilerplate_start(pdf_general_style)

    all_html_content += f'<h1 class="first_page_title">{fName}\'s Content Review Checklist. </h1>'

    all_html_content += f"""
    <div class="intro-page">
        <h2 style="text-indent: 4em"> Here's a full review checklist of everything needed for our <u> {style} content style</u>.</h2>
        <p>When reviewing your content, please double-check each guide, and make sure it alligns with our guidelines + review sheet :)</p>
    """

    current_category = None

    for row in useful_columns:
        #adding my page break  <-- improve later

        #defining values
        link = row["link"]
        notion_id = row["notion_id"]
        docName = row["name"]
        category = row["category"]
        edit = row["edit"]
        qa = row["qa"]

        print(current_category)
        #1. CREATING THE LIST
            #page container
        all_html_content += f'<div class="list">'

        # if category isnt being made already
        if category != current_category:
            all_html_content += f"""        
            <div class="category_title_checklist"> <br> <br>
            {category}
            </div> 
            """
            print("eeee \n \n \n \n")

        current_category = category

        #3. SETTING THE TITLE
        all_html_content += f"""
        <div class="document_title_checklist">
        {docName}
        </div>
        """


        #4. Document Link

        all_html_content += f"""<div class="qa_link">
        <a href="{link}" target="_blank">Link</a>
        </div>
        """

        
        #5. closing the list div and adding a newline

        all_html_content += """<br> <br>  </div>"""


    all_html_content += """
    <p> When Reviewing your content, please ensure that all of these are being followed! </p>
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
    id = upload_to_drive(temp_pdf_file_path, f'{style} Content Guidelines for {fName}.pdf', drive_folder_id)
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
