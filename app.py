from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import google.generativeai as genai
import PyPDF2

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", os.urandom(24))

# Read essay content from markdown file
with open(os.path.join('static', 'essay.md'), 'r', encoding='utf-8') as f:
    essay_markdown = f.read()

# Extract knowledge base from PDFs
def extract_text_from_pdfs(pdf_paths):
    text = ""
    for path in pdf_paths:
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    return text

pdf_files = [os.path.join('training_data', f) for f in os.listdir('training_data') if f.endswith('.pdf')]
knowledge_base = extract_text_from_pdfs(pdf_files)

# Set up Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

# At the top of your app.py, after extracting knowledge_base:
system_prompt = {
    "role": "user",
    "parts": []
}

if knowledge_base.strip():
    # Splitting the knowledge base into chunks of 500 characters each
    knowledge_base_chunks = [knowledge_base[i:i+500] for i in range(0, len(knowledge_base), 500)]

    # Constructing the system prompt with the knowledge base chunks
    for i, chunk in enumerate(knowledge_base_chunks):
        if i == 0:
            system_prompt["parts"].append({
                "text": (
                    "You are Edmund, an LLM meant for social good. Use the imported PDF files to guide your thinking, spanning the topics of climate, artificial intelligence, design, and more. They are not your only reference, but rather an inspiration and established baseline. Feel free to reference them where applicable, or similar works you’re aware of. Keep the articles' key takeaways in mind as you interact with the user to contribute (even minorly) to an equitable, fair future for society. With this, you should always consider the diversity of human thought and experience. Local/cultural practices are different throughout. Don’t be afraid to ask questions to better understand the users, figuring out what their practices are so you can deliver information in an appropriate manner. Still at the heart of it all, you’re an LLM. Therefore, make sure you answer questions appropriately given your original model, along with this information I’ve provided:\n\n"
                    + chunk
                )
            })
        else:
            system_prompt["parts"].append({
                "text": chunk
            })
else:
    # Fallback if no knowledge base is found
    system_prompt["parts"].append({
        "text": (
            "You are Edmund, an LLM meant for social good. Use your general knowledge to answer questions about climate, artificial intelligence, design, and more. Always consider the diversity of human thought and experience."
        )
    })

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

    # Always prepend the system prompt
    conversation_with_prompt = [system_prompt] + conversation

    response = model.generate_content(conversation_with_prompt)
    bot_message = response.text.strip()
    return jsonify({"message": bot_message})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
