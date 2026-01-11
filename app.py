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


# 🔁 Fallback (only if Gemini fails)
def fallback_experience(title, company, years):
    return f"""
{title} – {company} ({years})
• Delivered consistent performance in a fast-paced operational role
• Managed role-specific daily responsibilities with accuracy and ownership
• Coordinated with teams and stakeholders to maintain workflow efficiency
• Followed structured processes while meeting productivity expectations
• Demonstrated reliability, adaptability, and professional discipline
""".strip()


def generate_experience_block(title, company, years, responsibilities, language):
    prompt = f"""
You are a PROFESSIONAL HR AI built ONLY for resume writing.

THINK BEFORE WRITING (do not show thinking):
- Identify the job role and seniority
- Identify the industry from title/company
- Identify key responsibility areas from context
- Convert them into STRONG, NON-GENERIC resume bullets
- Ensure each bullet highlights a DIFFERENT skill or impact

STRICT RULES:
- No repeated ideas
- No generic phrases
- No filler content
- No copying the input text
- ATS-optimized language
- 6 to 8 bullet points
- Strong action verbs
- Sounds like written by an experienced professional

OUTPUT FORMAT:
- Bullet points only
- No headings
- Output ONLY in {language}

JOB DETAILS:
Title: {title}
Company: {company}
Duration: {years}

USER CONTEXT (for understanding only):
{responsibilities}
"""

    if model is None:
        return fallback_experience(title, company, years)

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        if not text or len(text) < 220:
            return fallback_experience(title, company, years)

        return f"{title} – {company} ({years})\n{text}"

    except Exception as e:
        print("Gemini error:", e)
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

        resume_output = f"""{name}

PROFESSIONAL EXPERIENCE
{chr(10).join(experience_sections)}
"""

    return render_template("index.html", resume=resume_output)


if __name__ == "__main__":
    app.run()
