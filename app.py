from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# ✅ Gemini API Key (hardcoded for now)
GEMINI_API_KEY = "AIzaSyDSHsNt7aA9cpLhszY6HOwq_PSXlPTItyw"


def generate_experience_points(raw_experience, output_language):
    prompt = f"""
You are an expert resume writer.

The user may give very short input like a job title.
You must intelligently expand it with realistic responsibilities.

Write 4–6 strong, professional, ATS-friendly bullet points.
Do NOT ask questions.
Do NOT mention assumptions.
Write ONLY in {output_language}.

User input:
{raw_experience}
"""

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()

        # ✅ Universal safe parsing
        if "candidates" in data and len(data["candidates"]) > 0:
            content = data["candidates"][0].get("content", {})
            parts = content.get("parts", [])
            if parts and "text" in parts[0]:
                return parts[0]["text"]

        if "error" in data:
            return f"AI Error: {data['error'].get('message')}"

        return "AI could not generate content. Please provide a little more detail."

    except Exception as e:
        return f"AI connection error: {str(e)}"


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
