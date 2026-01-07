from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

# 🔐 Read Gemini key from environment (Render-safe)
GEMINI_API_KEY = os.environ.get "AIzaSyDSHsNt7aA9cpLhszY6HOwq_PSXlPTItyw"


def generate_experience_points(raw_experience, output_language):
    prompt = f"""
You are a professional resume writer.

Convert the following job experience into 3–5 professional resume bullet points.
Write ONLY in {output_language}.

Experience:
{raw_experience}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(url, json=payload, timeout=30)

    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


@app.route("/", methods=["GET", "POST"])
def home():
    resume_text = ""

    if request.method == "POST":
        name = request.form.get("name")
        experience = request.form.get("experience")
        language = request.form.get("language")

        ai_text = generate_experience_points(experience, language)

        resume_text = f"""
Name: {name}

Professional Experience:
{ai_text}
"""

    return render_template("index.html", resume=resume_text)


if __name__ == "__main__":
    app.run()