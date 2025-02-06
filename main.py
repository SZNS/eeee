from flask import Flask, request, jsonify
import markdown
import functions_framework

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']

    text = file.read().decode('utf-8')
    markdown_text = markdown.markdown(text)

    return jsonify({'message': f'File parsed: {markdown_text}'}), 200

    #Commenting this out for now for pdf support 
    # pdf_document = pymupdf.open(stream=file.read(), filetype="pdf")
    # text = ""
    # for page_num in range(pdf_document.page_count):
    #     page = pdf_document.load_page(page_num)
    #     text += page.get_text()
    #     print(text)

def openai_api(markdown_text):
    #openai api with parsed markdown text
    return jsonify({'message': 'OpenAI API is not implemented yet'}), 200

def linear_api(openai_response):
    #create linear project and issues with openai response
    return jsonify({'message': 'Linear API is not implemented yet'}), 200

@functions_framework.http
def main(request):
    return upload()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)