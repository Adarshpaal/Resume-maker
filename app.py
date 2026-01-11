from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

# 🔑 Gemini API key (testing OK)
genai.configure(api_key="AIzaSyDSHsNt7aA9cpLhszY6HOwq_PSXlPTItyw")

# ✅ Load Gemini model safely
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception:
    model = None


# 🔁 Fallback (ONLY if Gemini fails)
def fallback_experience(title, company, years):
    return f"""
• Served as {title} at {company}, responsible for day-to-day operations  
• Coordinated tasks to ensure smooth workflow and operational efficiency  
• Maintained accuracy, discipline, and adherence to company standards  
• Supported team members and assisted supervisors in daily activities  
• Demonstrated reliability, accountability, and continuous learning
""".strip()


def generate_experience_block(title, company, years, language):
    prompt = f"""
You are a senior HR manager and ATS resume specialist.

Write PROFESSIONAL resume bullet points for the following role.

STRICT RULES:
- Role-specific responsibilities (NO generic lines)
- Use strong action verbs
- Add measurable impact where realistic
- ATS-friendly language
- 6–8 bullet points
- Avoid phrases like "assisted team", "followed rules"
- Output ONLY in {language}

Job Title: {title}
Company: {company}
Experience Duration: {years}
"""

    if model is None:
        return fallback_experience(title, company, years)

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        if not text or len(text) < 150:
            return fallback_experience(title, company, years)

        return text

    except Exception:
        return fallback_experience(title, company, years)


@app.route("/", methods=["GET", "POST"])
def home():
    resume_output = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        language = request.form.get("language", "English")

        titles = request.form.getlist("title[]")
        companies = request.form.getlist("company[]")
        years = request.form.getlist("years[]")

        experience_sections = []

        for i in range(len(titles)):
            if titles[i].strip():
                section = generate_experience_block(
                    titles[i].strip(),
                    companies[i].strip(),
                    years[i].strip(),
                    language
                )
                experience_sections.append(f"""
{titles[i]} – {companies[i]} ({years[i]})
{section}
""")

        resume_output = f"""
Name: {name}

PROFESSIONAL EXPERIENCE
{chr(10).join(experience_sections)}
"""

    return render_template("index.html", resume=resume_output)


if __name__ == "__main__":
    app.run()
