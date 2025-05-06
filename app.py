from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", os.urandom(24))

# Read essay content from markdown file
with open(os.path.join('static', 'essay.md'), 'r', encoding='utf-8') as f:
    essay_markdown = f.read()

# Set up Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

# Serve the main page
@app.route("/")
def index():
    return render_template("index.html", essay=essay_markdown)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    conversation = data.get("conversation")
    if not conversation or not isinstance(conversation, list):
        return jsonify({"error": "No conversation provided"}), 400
    response = model.generate_content(conversation)
    bot_message = response.text.strip()
    return jsonify({"message": bot_message})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
