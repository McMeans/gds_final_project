from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    messages = [
        "Hello! How can I help you today?",
        "I'm here to chat! What's on your mind?",
        "Nice to meet you! What would you like to talk about?",
        "Hi there! I'm ready to have a conversation.",
        "Greetings! How can I assist you?"
    ]
    
    random_message = random.choice(messages)
    return jsonify({"message": random_message})

if __name__ == '__main__':
    app.run(debug=True) 