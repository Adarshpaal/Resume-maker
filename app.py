from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

# 🔑 Gemini API key (testing only – rotate later)
genai.configure(api_key="AIzaSyDSHsNt7aA9cpLhszY6HOwq_PSXlPTItyw")

# ✅ Stable free model
model = genai.GenerativeModel("gemini-1.5-flash")


def generate_experience_points(raw_experience, output_language):
    if not raw_experience.strip():
        return "Please enter your job role or experience."

    prompt = f"""
You are an expert resume writer.

The user may provide very short input like:
"computer operator", "data entry", "office assistant"

Your job:
- Expand it professionally
- Assume realistic responsibilities
- Make it ATS-friendly
- Write 4–6 bullet points
- Use strong action verbs
- Output ONLY in {output_language}

User input:
{raw_experience}
"""

    try:
        response = model.generate_content(prompt)

        # ✅ SAFE extraction
        if hasattr(response, "text") and response.text:
            return response.text.strip()

        return (
            "• Managed daily computer and office operations\n"
            "• Performed accurate data entry and record maintenance\n"
            "• Prepared reports and documents using office software\n"
            "• Assisted staff with administrative and technical tasks\n"
            "• Ensured timely completion of assigned responsibilities"
        )

    except Exception as e:
        return "AI could not generate content at the moment. Please try again."


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
