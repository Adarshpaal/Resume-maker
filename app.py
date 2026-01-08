from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

# 🔑 Gemini API key (TEMP – OK for testing)
genai.configure(api_key="AIzaSyDSHsNt7aA9cpLhszY6HOwq_PSXlPTItyw")

# ✅ Load Gemini model safely
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception:
    model = None


# 🔁 SMART FALLBACK (never shows blank or error)
def fallback_resume(experience, language):
    return f"""
• Worked as a {experience}, managing daily job responsibilities
• Performed tasks efficiently while maintaining accuracy and productivity
• Supported team operations and assisted with workflow coordination
• Followed organizational procedures and safety guidelines
• Demonstrated reliability, adaptability, and willingness to learn
""".strip()


def generate_experience_points(experience, output_language):
    # 🔥 IMPORTANT: normalize user input (PASTE HERE)
    experience = experience.lower().strip()

    prompt = f"""
You are a senior HR professional and ATS resume expert.

The user may write job experience very casually, such as:
"computer operator", "picker at shiprocket", "warehouse helper", "data entry"

Your task:
- Identify the real job role and industry
- Expand it into PROFESSIONAL resume bullet points
- Add role-specific responsibilities (not generic)
- Use strong action verbs
- Make it ATS-friendly
- Write 6–8 impactful bullet points
- Avoid weak lines like "assisted team" or "followed rules"
- Output ONLY in {output_language}

User job experience:
{experience}
"""

    if model is None:
        return fallback_resume(experience, output_language)

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # If Gemini gives weak or tiny response
        if not text or len(text) < 80:
            return fallback_resume(experience, output_language)

        return text

    except Exception as e:
        print("Gemini error:", e)
        return fallback_resume(experience, output_language)


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
