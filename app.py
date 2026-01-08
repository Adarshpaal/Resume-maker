from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

# 🔑 Gemini API Key (TEMPORARY – works immediately)
genai.configure(api_key="AIzaSyDSHsNt7aA9cpLhszY6HOwq_PSXlPTItyw")

# ✅ Correct free model
model = genai.GenerativeModel("gemini-1.5-flash")


def generate_experience_points(raw_experience, output_language):
    prompt = f"""
You are a professional resume writer.

The user may write job experience in short or casual form
(for example: "computer operator", "data entry", "office work").

Your task:
- Expand it professionally
- Add realistic responsibilities
- Make it ATS-friendly
- Write 4–6 crisp bullet points
- Use strong action verbs
- Output ONLY in {output_language}

User input:
{raw_experience}
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return "AI could not generate content. Please try again."


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
