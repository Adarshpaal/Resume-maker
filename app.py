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
You are an elite HR professional who writes resumes that impress senior recruiters.

You MUST follow these rules strictly:

ROLE ANALYSIS (internal):
- Identify the exact job function (example: warehouse ops vs cinema ops)
- Identify the working environment (warehouse / cinema / retail / logistics)
- Identify the primary responsibility domain (inventory, safety, customers, systems, people)

OUTPUT RULES (MANDATORY):
- Each job MUST have UNIQUE bullet points
- You are FORBIDDEN from reusing the same bullet idea across different jobs
- Every bullet must clearly reflect the job environment
- If the job is cinema-related, mention crowd safety, customer experience, compliance
- If the job is warehouse-related, mention inventory flow, logistics, accuracy, coordination
- NO generic operational statements
- NO vague phrases like "fast-paced role" or "handled responsibilities"
- Use professional, ATS-optimized language
- 6 to 8 bullet points ONLY
- Bullet points ONLY, no headings
- Output ONLY in {language}

JOB DETAILS:
Title: {title}
Company: {company}
Duration: {years}

USER CONTEXT (for understanding only, DO NOT COPY):
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
