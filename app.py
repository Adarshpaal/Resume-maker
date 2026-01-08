from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# ⚠️ Hardcoded Gemini API Key (works, but not secure)
GEMINI_API_KEY = "AIzaSyDSHsNt7aA9cpLhszY6HOwq_PSXlPTItyw"


def generate_experience_points(raw_experience, output_language):
    prompt = f"""
You are an expert resume writer and career coach.

The user may provide very short or unclear job information.
You must intelligently EXPAND it by assuming common responsibilities
for that role and write a strong professional experience section.

Rules:
- Write 4–6 crisp bullet points
- Use action verbs
- Make it ATS-friendly
- Do NOT ask questions
- Do NOT mention assumptions
- Write ONLY in {output_language}

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
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()

        if (
            "candidates" in data
            and len(data["candidates"]) > 0
            and "content" in data["candidates"][0]
        ):
            return data["candidates"][0]["content"]["parts"][0]["text"]

        return "AI could not generate content. Please provide a little more detail."

    except Exception:
        return "Error connecting to AI service. Please try again."


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
