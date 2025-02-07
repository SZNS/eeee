from flask import Flask, request, jsonify
import markdown
import functions_framework
from openai import OpenAI
from linear.LinearClient import write_to_linear
import os
import json

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']

    text = file.read().decode('utf-8')
    markdown_text = markdown.markdown(text)

    opena_ai_resp = openai_api(markdown_text)

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "project_tasks_response",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "project": {"type": "string"},
                        "tasks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "assignee": {"type": "string"},
                                    "due_date": {"type": "string"},
                                    "description": {"type": "string"},
                                    "subtasks": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                     },
                                     "state": {"type": "string"},
                                },
                                "required": ["title", "assignee", "due_date", "description", "subtasks", "state"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["project", "tasks"],
                    "additionalProperties": False
                }
            }
        }

    chat_completion = client.chat.completions.create(
        messages=[
        {"role": "developer", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": f"{markdown_text}"
        }
        ],
        model="gpt-4o-mini",
        response_format=response_format
    )


    structured_response = chat_completion.choices[0].message.content

    json_resp = json.loads(structured_response)

    linearresp = write_to_linear(json_resp)

    print(linearresp)

    # # Write the response to output.json file.
    # with open('output.json', 'w') as output_file2:
    #     json.dump(json_resp, output_file2, indent=2)

    return jsonify({'message': f'File parsed: {json_resp}'}), 200

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