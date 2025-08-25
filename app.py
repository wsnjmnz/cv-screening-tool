import streamlit as st
import re
from datetime import datetime

st.set_page_config(page_title="Advanced AI-Style CV Screener", layout="wide")

st.title("📄 Advanced AI-Style CV Screener (Paste Only)")

# Input boxes
st.subheader("Enter Non-Negotiable Requirements (one per line)")
requirements = st.text_area(
    "Requirements",
    height=200,
    placeholder="Example:\n- 2+ years in IT support\n- Experience with Microsoft 365\n- Strong communication skills"
)

st.subheader("Paste Candidate CV")
cv_text = st.text_area(
    "Candidate CV",
    height=400,
    placeholder="Paste the full resume/CV text here"
)

def extract_years(cv_text):
    # Extract years from ranges like 2016-2022 or 2016 – Present
    matches = re.findall(r'(\d{4})\s*[-–]\s*(\d{4}|Present)', cv_text)
    total = 0
    for start, end in matches:
        start = int(start)
        end = datetime.now().year if end.lower() == "present" else int(end)
        total += end - start
    return total

def detect_job_hopper(cv_text):
    # Count number of distinct job stints
    matches = re.findall(r'(\d{4})\s*[-–]\s*(\d{4}|Present)', cv_text)
    if len(matches) >= 4:  # heuristic: 4+ short stints = job hopper
        return "Yes"
    else:
        return "No"

def score_requirement(req, cv_text):
    # Full match
    if req.lower() in cv_text.lower():
        return 5, f"✅ Fully matched: candidate clearly meets '{req}'."
    else:
        # Partial match based on words
        words = req.lower().split()
        matches = sum(1 for w in words if w in cv_text.lower())
        score = round((matches / len(words)) * 5)
        if score < 1:
            score = 1
        reason = f"⚠️ Partial match: '{req}' only partially found in CV." if score < 5 else f"✅ Fully matched: '{req}'"
        return score, reason

# Screening logic
if st.button("Screen CV"):
    if not requirements.strip() or not cv_text.strip():
        st.warning("⚠️ Please enter both requirements and a candidate CV.")
    else:
        reqs = [r.strip() for r in requirements.split("\n") if r.strip()]
        results = []
        total_score = 0
        reasoning = []

        for req in reqs:
            score, reason = score_requirement(req, cv_text)
            results.append(f"{req} – {score}")
            reasoning.append(reason)
            total_score += score

        average_score = round(total_score / len(reqs), 2)
        job_hopper = detect_job_hopper(cv_text)
        years_exp = extract_years(cv_text)

        # Determine overall result
        if average_score >= 4 and job_hopper == "No":
            overall_result = "PASS"
            summary = "Candidate meets most requirements, strong technical skills, reliable experience."
        elif average_score >= 3:
            overall_result = "POTENTIAL"
            summary = "Candidate partially meets requirements, shows transferable skills, may need development."
        else:
            overall_result = "FAIL"
            summary = "Candidate does not meet key requirements."

        # Display results
        st.subheader("Screening Results")
        for r, reason in zip(results, reasoning):
            st.write(r)
            st.write(f"   - {reason}")

        st.write(f"\n**Job Hopper:** {job_hopper}")
        st.write(f"**Estimated Years of Experience:** {years_exp}")
        st.write(f"\n**Average Score:** {average_score}")
        st.write(f"**Overall Result:** {overall_result}")
        st.write(f"**Summary:** {summary}")
