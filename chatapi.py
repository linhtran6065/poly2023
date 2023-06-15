from flask import Flask, request, jsonify
import openai
from flask_cors import CORS, cross_origin


openai.api_key = "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"
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


messages = []
system_msg = "You are a psychologist. Your task is to chat with users. Maximum 5 answers. If the conversation get too long, tell them you can help they reach to master users or professionals"
messages.append({"role": "system", "content": system_msg})


@app.route('/getchat/<msg>', methods=['GET', 'POST'])
def getchat(msg):
    message = msg
    messages.append({"role": "user", "content": message})  # input cua user
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages)
    reply = response["choices"][0]["message"]["content"]  # reply of chatgpt
    messages.append({"role": "assistant", "content": reply})
    response = jsonify(reply)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
