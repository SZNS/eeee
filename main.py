from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']

    markdown_text = file.read().decode('utf-8')
    print(markdown_text)

    return jsonify({'message': 'File parsed'}), 200
    #Commenting this out for now for pdf support 
    # pdf_document = pymupdf.open(stream=file.read(), filetype="pdf")
    # text = ""
    # for page_num in range(pdf_document.page_count):
    #     page = pdf_document.load_page(page_num)
    #     text += page.get_text()
    #     print(text)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)