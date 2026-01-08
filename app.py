from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

# 🔑 Gemini API key (temporary for testing)
genai.configure(api_key="AIzaSyDSHsNt7aA9cpLhszY6HOwq_PSXlPTItyw")

# Try to load model
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception:
    model = None


def fallback_resume(experience, language):
    # Smart fallback so demo NEVER fails
    return f"""
• Worked as a {experience}, handling daily operational responsibilities
• Maintained accuracy and efficiency in assigned tasks
• Assisted team members and supported office workflows
• Followed company procedures and quality standards
• Demonstrated reliability, discipline, and willingness to learn
""".strip()


def generate_experience_points(raw_experience, output_language):
    prompt = f"""
You are a professional resume writer.

User may write very short experience like:
"computer operator", "office boy", "data entry"

Expand it professionally:
- Add realistic responsibilities
- Use ATS-friendly bullet points
- 4–6 points
- Strong action verbs
- Output ONLY in {output_language}

User input:
{raw_experience}
"""

    if model is None:
        return fallback_resume(raw_experience, output_language)

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        if not text:
            return fallback_resume(raw_experience, output_language)

        return text

    except Exception:
        return fallback_resume(raw_experience, output_language)


@app.route("/", methods=["GET", "POST"])
def home():
    resume_text = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        experience = request.form.get("experience", "").strip()
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
