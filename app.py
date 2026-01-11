from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

# 🔑 Gemini API key (testing)
genai.configure(api_key="AIzaSyDSHsNt7aA9cpLhszY6HOwq_PSXlPTItyw")

# Load Gemini safely
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception:
    model = None


def fallback_experience(title, company, years, responsibilities):
    return f"""
{title} – {company} ({years})
• Managed core responsibilities related to {responsibilities}
• Executed daily operational tasks with accuracy and efficiency
• Coordinated with cross-functional teams to meet performance goals
• Maintained compliance with company processes and quality standards
• Demonstrated accountability, adaptability, and continuous improvement
""".strip()


def generate_experience_block(title, company, years, responsibilities, language):
    prompt = f"""
You are a senior HR manager and ATS resume expert.

Create a PROFESSIONAL resume experience section.

STRICT RULES:
- Understand the ROLE and INDUSTRY
- Write role-specific responsibilities (NOT generic)
- Use strong action verbs
- Add measurable impact where realistic
- ATS-friendly language
- 6–8 bullet points
- No weak phrases like "assisted team" or "followed rules"
- Output ONLY in {language}

Job Title: {title}
Company: {company}
Duration: {years}

User responsibilities / context:
{responsibilities}
"""

    if model is None:
        return fallback_experience(title, company, years, responsibilities)

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        if not text or len(text) < 200:
            return fallback_experience(title, company, years, responsibilities)

        return f"{title} – {company} ({years})\n{text}"

    except Exception:
        return fallback_experience(title, company, years, responsibilities)


@app.route("/", methods=["GET", "POST"])
def home():
    resume_output = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        language = request.form.get("language", "English")

        titles = request.form.getlist("title[]")
        companies = request.form.getlist("company[]")
        years = request.form.getlist("years[]")
        responsibilities = request.form.getlist("responsibilities[]")

        experience_sections = []

        for i in range(len(titles)):
            if titles[i].strip():
                block = generate_experience_block(
                    titles[i].strip(),
                    companies[i].strip(),
                    years[i].strip(),
                    responsibilities[i].strip(),
                    language
                )
                experience_sections.append(block)

        resume_output = f"""
{name}

PROFESSIONAL EXPERIENCE
{chr(10).join(experience_sections)}
"""

    return render_template("index.html", resume=resume_output)


if __name__ == "__main__":
    app.run()
