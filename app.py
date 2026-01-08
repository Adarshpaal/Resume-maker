from flask import Flask, render_template, request
import google.generativeai as genai
import os

app = Flask(__name__)

# ✅ Read API key from environment (Render-safe)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ✅ Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Load model (this WORKS with free keys)
model = genai.GenerativeModel("gemini-1.5-flash")


def generate_experience_points(raw_experience, output_language):
    prompt = f"""
You are a professional resume writer.

The user will describe their job briefly (even one line).
Your task:
- Expand it professionally
- Add realistic responsibilities
- Write 4–6 crisp bullet points
- Use strong resume language
- Output ONLY in {output_language}

User input:
{raw_experience}
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI Error: {str(e)}"


@app.route("/", methods=["GET", "POST"])
def home():
    resume_text = ""

    if request.method == "POST":
        name = request.form.get("name", "")
        experience = request.form.get("experience", "")
        language = request.form.get("language", "English")

        ai_text = generate_experience_points(experience, language)

        resume_text = f"""
Name: {name}

Professional Experience:
{ai_text}
"""

    return render_template("index.html", resume=resume_text)


if __name__ == "__main__":
    app.run()
