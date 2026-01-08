from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# ⚠️ Hardcoded Gemini API key (works, not secure)
GEMINI_API_KEY = "AIzaSyDSHsNt7aA9cpLhszY6HOwq_PSXlPTItyw"


def generate_experience_points(raw_experience, output_language):
    prompt = f"""
You are a professional resume writer.

The user may provide very short job information.
You must intelligently expand it with realistic responsibilities.

Write 4–6 strong, ATS-friendly bullet points.
Do NOT ask questions.
Do NOT mention assumptions.
Write ONLY in {output_language}.

User input:
{raw_experience}
"""

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-pro:generateContent?key={GEMINI_API_KEY}"
    )

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()

        # ✅ DEBUG SAFETY (handles all Gemini formats)
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]

            if "content" in candidate and "parts" in candidate["content"]:
                parts = candidate["content"]["parts"]
                if len(parts) > 0 and "text" in parts[0]:
                    return parts[0]["text"]

        # If Gemini responds with error message
        if "error" in data:
            return f"AI Error: {data['error'].get('message', 'Unknown error')}"

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
