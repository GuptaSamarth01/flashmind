import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import openai
from flask import render_template
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# openai.api_key = "YOUR_API_KEY"

genai.configure(api_key="AIzaSyBl48VjFXhxRiZQZjVsAqzudVhaNxqLxT8")

def extract_text_from_pdf(file):
    try:
        file.stream.seek(0)
        doc = fitz.open(stream=file.read(), filetype="pdf")

        text = ""
        for page in doc:
            text += page.get_text("text")

        # CLEAN TEXT
        text = text.replace("\n", " ").strip()

        print("EXTRACTED TEXT:", text[:500])

        return text if len(text) > 50 else "This is a sample text about photosynthesis and plants."

    except Exception as e:
        print("PDF ERROR:", e)
        return "Photosynthesis is the process by which plants make food using sunlight."

# def generate_flashcards(text):
#     model = genai.GenerativeModel("gemini-pro")
#     prompt = f"""
#     You are a great teacher.

#     Convert the following text into EXACTLY 10 flashcards.

#     STRICT RULES:
#     - Use ONLY this format:
#     Q: question
#     A: answer
#     - No numbering
#     - No extra explanation
#     - Each question must be clear and useful
#     - Cover concepts, definitions, and examples

#     Text:
#     {text[:2000]}
#     """

#     response = model.generate_content(prompt)

#     print("GEMINI RAW OUTPUT:\n", response.text)  # 👈 DEBUG

#     return response.text

import re

def generate_flashcards(text):
    sentences = text.split(".")
    cards = []

    for s in sentences:
        s = s.strip()

        if len(s) < 40:
            continue

        # Try to detect definition sentences
        if " is " in s:
            parts = s.split(" is ", 1)
            subject = parts[0].strip()
            answer = s

            question = f"What is {subject}?"

        # Try "occurs in", "happens in"
        elif " occurs in " in s or " happens in " in s:
            question = "Where does this process occur?"
            answer = s

        # Try "used for", "responsible for"
        elif " used for " in s or " responsible for " in s:
            question = "What is the function described?"
            answer = s

        else:
            # fallback
            words = s.split()
            key = " ".join(words[:4])
            question = f"Explain: {key}..."

            answer = s

        cards.append({
            "question": question,
            "answer": answer,
            "score": 0
        })

        if len(cards) >= 10:
            break

    return cards

@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files["file"]

        text = extract_text_from_pdf(file)
        flashcards = generate_flashcards(text)

        return jsonify({"flashcards": flashcards})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500

# @app.route("/upload", methods=["POST"])
# def upload():
#     return jsonify({
#         "flashcards": """
#         Q: What is AI?
#         A: Artificial Intelligence

#         Q: What is ML?
#         A: Machine Learning
#         """
#     })

@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))