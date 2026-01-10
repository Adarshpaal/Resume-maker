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


# 🔁 ROLE-AWARE FALLBACK (used ONLY if Gemini fails)
def fallback_resume(role, language):
    return f"""
• Held the position of {role} with responsibility for core role-specific tasks
• Executed duties using industry-standard tools and operational procedures
• Maintained accuracy, efficiency, and accountability under deadlines
• Coordinated with cross-functional teams to meet business objectives
• Identified and resolved operational issues proactively
• Demonstrated strong work ethic, adaptability, and professional growth
""".strip()


def generate_experience_points(experience, output_language):
    # ✅ NORMALIZE INPUT (THIS IS WHERE IT GOES)
    experience = experience.strip().lower()

    # 🔥 Split multiple roles correctly
    experience_blocks = [
        e.strip()
        for e in experience.replace("\n", ".").split(".")
        if len(e.strip()) > 5
    ]

    final_output = []

    for block in experience_blocks:
        prompt = f"""
You are a senior hiring manager who has hired people for THIS EXACT ROLE.

Candidate job description:
"{block}"

STRICT RULES:
- DO NOT write generic duties
- DO NOT reuse same bullet structure across roles
- Infer tools, systems, KPIs, environment from role
- Write REALISTIC, role-specific work
- Use strong action verbs
- ATS-friendly language
- 6–8 bullets
- Each bullet must be UNIQUE and professional
- Output ONLY in {output_language}

BAD (do NOT use):
❌ daily operations
❌ supported team
❌ followed policies

GOOD (role dependent):
✔ inventory reconciliation (warehouse)
✔ staff scheduling & escalation handling (manager)
✔ ERP / WMS / CRM usage
✔ reporting, audits, SLA tracking

NOW WRITE PROFESSIONAL EXPERIENCE:
"""

        if model is None:
            final_output.append(fallback_resume(block, output_language))
            continue

        try:
            response = model.generate_content(prompt)
            text = response.text.strip()

            # 🚨 QUALITY GATE (prevents weak output)
            if (
                not text
                or len(text) < 200
                or "daily operations" in text.lower()
                or "supported" in text.lower()
            ):
                raise ValueError("Weak Gemini output")

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
