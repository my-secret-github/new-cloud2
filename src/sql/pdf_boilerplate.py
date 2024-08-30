def html_boilerplate_start(pdf_general_style):
    boilerplate = f"""
    <!DOCTYPE html>
    <html lang="en">

    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> MyTitle </title>

    <style>  {pdf_general_style} </style>
    <link href="pdf_css/notion_blocks.css" rel="stylesheet">    
    </head>
    <body>

    """
    return boilerplate