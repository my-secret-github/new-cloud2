from flask import Flask, request, jsonify, render_template
from from_sql import input_query
from interpret_sql import interpret_headers, interpret_rows
from organize_pdf import json_to_py
from pdf_compiler import pdf_ready
from pdf_create_sql import pdf_create_main

"""import os
try:
    import src.pdf_create_sql  # Attempt to import
    modpath = os.path.abspath(src.pdf_create_sql.__file__)
    print(f"Module found at: {modpath}")
except ModuleNotFoundError:
    # This will show where Python was trying to find the module
    print("Module not found.")
    modpath = os.path.abspath('src/pdf_create_sql.py')  # Construct the expected path
    print(f"Was looking for: {modpath}")"""

bucket_name = 'amora_img_bucket'


app = Flask(__name__)

def main_headers(headers):
    try:
        data = input_query(headers)
        interpreted = interpret_headers(data)
        return interpreted
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e), 500

def rows_display(rows):
    try:
        data = input_query(rows)
        interpreted = interpret_rows(data)
        return interpreted
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e), 500

@app.route("/")
def data():
    try:
        # all columns headers = "show columns from guidelines"
        headers = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'guidelines' AND COLUMN_NAME IN ('g_id', 'g_name', 'g_link', 'g_category', 'mandatory');"
        headers_result = main_headers(headers)
        rows = "select g_id,g_name, g_link, g_category, mandatory from guidelines"
        rows_result = rows_display(rows)
    except Exception as e:
        result = f"Submit a query to get results. Error: {e}"
        headers_result = ""
        rows_result = ""

    return render_template("index.html", headers=headers_result, rows=rows_result)


@app.route('/process', methods=['POST'])
def process_data():
    try:
        data = request.json.get('data')  # Retrieve the data from the JSON payload
        fName = request.json.get('fName')
        style = request.json.get('style')

        if data is None:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        # Convert each guide ID in the list to uppercase
        
        guides_full = json_to_py(data)
        guides_ready = pdf_ready(guides_full)
        
        useful_columns = pdf_create_main(guides_ready)

        from pdf_html import create_pdf_from_pages

        print(fName)

        pdf_confirmation = create_pdf_from_pages(useful_columns, fName, style)
        

        #print(f'it should have been confirmed from {pdf_confirmation}')
        print(pdf_confirmation)

        return jsonify(pdf_confirmation)


    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/processQa', methods=['POST'])
def process_data_qa():
        try:
            from qa_pdf import qa_pdf

            data = request.json.get('data')
            fName = request.json.get('fName')
            style = request.json.get('style')
            if data is None:
                return jsonify({'status': 'error', 'message': 'No Data Provided..'})


            guides_full = json_to_py(data)
            guides_ready = pdf_ready(guides_full)
            print(guides_ready)
            useful_columns = pdf_create_main(guides_ready)
            print("hello")
            pdf_confirmation = qa_pdf(useful_columns, fName, style)
            return jsonify(pdf_confirmation)

        except Exception as e:
            return jsonify(({'status': 'error', 'message': str(e)}))


progress = "0%"  # Store the progress here

@app.route('/update_progress', methods=['POST'])
def update_progress():
    global progress
    data = request.get_json()
    progress = data.get('amount', '0%')
    return jsonify({"status": "success", "amount": progress})


@app.route('/get_progress', methods=['GET'])
def get_progress():
    global progress
    return jsonify({"progress": progress})


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8080)
