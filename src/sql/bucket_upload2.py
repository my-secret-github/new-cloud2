import os
from google.cloud import storage
import hashlib
import urllib
import requests
from sql.secret_keys_SQL import notion_headers


BASE_URL = "https://www.file.notion.so"


def initialize_storage_client():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service-key-google-cloud.json'
    return storage.Client()

def create_bucket_if_not_exists(client, bucket_name):
    bucket = client.bucket(bucket_name)
    if not bucket.exists():
        bucket.location = 'US'
        bucket = client.create_bucket(bucket)
    return bucket

def upload_to_bucket(file_name, file_content, bucket_name):
    try:
        client = initialize_storage_client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.upload_from_string(file_content)
        blob.make_public()
        public_url = blob.public_url
        #print(f'Uploaded {file_name} to {bucket_name}. Public URL: {public_url}')
        return public_url
    except Exception as e:
        print(f'Error uploading file to bucket: {e}')
        return None



def upload_image_to_bucket(image_url, bucket_name):
    final_url = resolve_final_url(image_url)
    if not final_url:
        return ""

    if "notion.so" in final_url:
        file_name = get_short_filename_notion(final_url)
        #print(f"Generated filename for Notion URL: {file_name}")
    else:
        file_name = hashlib.md5(final_url.encode('utf-8')).hexdigest() + ".png"
        #print(f"Generated filename for non-Notion URL: {file_name}")

    file_content = download_final_file(final_url)
    if not file_content:
        return ""

    try:
        public_url = upload_to_bucket(file_name, file_content, bucket_name)
        #print(f"Uploaded file to bucket. Public URL: {public_url}")
        return public_url
    except Exception as e:
        print(f"Error uploading file to bucket: {e}")
        return ""
    

def download_file_from_bucket(blob_name, file_path, bucket_name):
    try:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        with open(file_path, 'wb') as f:
            client.download_blob_to_file(blob, f)
        #print(f'downloaded {blob_name} from {bucket_name} to {file_path}')
        return blob.public_url
    except Exception as e:
        print(e)
        return False



    
def resolve_final_url(url):
    if url.startswith('/api/attachments.redirect'):
        url = urllib.parse.urljoin(BASE_URL, url)
        #print(f"Updated URL to: {url}")
    try:
        session = requests.Session()
        response = session.head(url, headers=notion_headers, allow_redirects=True)
        final_url = response.url
        return final_url
    except requests.exceptions.RequestException as e:
        #print(f"Error resolving URL {url}: {e}")
        return None
    
    
def get_short_filename_notion(url):
    url_no_params = url.split("?")[0]  # Remove query parameters
    hash_object = hashlib.sha256(url_no_params.encode())
    return hash_object.hexdigest()[:10] + os.path.splitext(url_no_params)[-1]

def download_final_file(url):
    #print(f"Downloading file from final URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        #print(f"Downloaded file content from: {url}")
        return response.content
    except Exception as e:
        print(f"Error downloading file from {url}: {e}")
        return None
    
