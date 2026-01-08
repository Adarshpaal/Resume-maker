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


# 🔁 SMART FALLBACK (never shows error / blank)
def fallback_resume(experience, language):
    return f"""
• Worked as a {experience} with responsibility for daily operations
• Managed assigned tasks with accuracy and time efficiency
• Coordinated with team members to ensure smooth workflow
• Followed organizational policies, safety, and quality standards
• Demonstrated reliability, adaptability, and continuous learning mindset
""".strip()


def generate_experience_points(experience, output_language):
    experience = experience.strip()

    # 🔥 Split multiple job experiences properly
    experience_blocks = [
        e.strip()
        for e in experience.replace("\n", ".").split(".")
        if len(e.strip()) > 5
    ]

    final_output = []

    for block in experience_blocks:
        prompt = f"""
You are a senior HR manager and ATS resume expert.

The user may write job experience casually or poorly.

Your task:
- Identify the correct job role and industry
- Rewrite it as a PROFESSIONAL resume section
- Add realistic, role-specific responsibilities
- Avoid generic or weak points
- Use strong action verbs
- Make it ATS-friendly
- Write 6–8 impactful bullet points
- Output ONLY in {output_language}

User job experience:
{block}
"""

        if model is None:
            final_output.append(fallback_resume(block, output_language))
            continue

        try:
            response = model.generate_content(prompt)
            text = response.text.strip()

            # Weak response protection
            if not text or len(text) < 120:
                final_output.append(fallback_resume(block, output_language))
            else:
                final_output.append(text)

        except Exception as e:
            print("Gemini error:", e)
            final_output.append(fallback_resume(block, output_language))

    return "\n\n".join(final_output)


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
