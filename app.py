from flask import Flask, render_template, request, jsonify
import vertexai
from vertexai.preview.language_models import ChatModel
import os
import google.cloud.logging
from dotenv import load_dotenv
from google.oauth2 import service_account


load_dotenv()

app = Flask(__name__)
PROJECT_ID = os.environ.get('GCP_PROJECT') #Your Google Cloud Project ID
LOCATION = os.environ.get('GCP_REGION')   #Your Google Cloud Project Region

# optional: if you want to use a service account other than the default one
credentials = service_account.Credentials.from_service_account_file('service-account-key.json')

client = google.cloud.logging.Client(project=PROJECT_ID, credentials=credentials)
client.setup_logging()

LOG_NAME = "flask-app-internal-logs"
logger = client.logger(LOG_NAME)

vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)

def load_context_from_text_file(filename):
    with open(filename, 'r') as file:
        return file.read()

def create_session():
    chat_model = ChatModel.from_pretrained("chat-bison@001")
    chat = chat_model.start_chat(context=load_context_from_text_file("context.txt"))
    return chat

def response(chat, message):
    parameters = {
        "temperature": 0.1,
        "max_output_tokens": 1024,
        "top_p": 0.8,
        "top_k": 40
    }
    result = chat.send_message(message, **parameters)
    return result.text

@app.route('/')
def index():
    ###
    return render_template('index.html')

@app.route('/palm2', methods=['GET', 'POST'])
def vertex_palm():
    user_input = ""
    if request.method == 'GET':
        user_input = request.args.get('user_input')
    else:
        user_input = request.form['user_input']
    logger.log(f"Starting chat session...")
    chat_model = create_session()
    logger.log(f"Chat Session created")
    content = response(chat_model,user_input)
    return jsonify(content=content)

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')