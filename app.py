import streamlit as st
import json
import os
import hashlib
from datetime import datetime
import re
import pandas as pd

# ----- CONFIG -----
APP_TITLE = "AI CV SCREENER"
SCREENING_SUBTITLE = "Paste candidate CV and your non-negotiable requirements below"
REQUIREMENTS_LABEL = "Enter Non-Negotiable Requirements (one per line)"
CV_LABEL = "Paste Candidate CV"
SEARCH_SUBTITLE = "Search and download candidates based on keywords in their CVs"
DOWNLOAD_BUTTON_TEXT = "⬇️ Download CSV of Shortlisted Candidates"

st.set_page_config(page_title=APP_TITLE, layout="wide")

# File to store CVs
DB_FILE = "candidates.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump([], f)

# ----- UTILITY FUNCTIONS -----
def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def hash_cv(cv_text):
    return hashlib.md5(cv_text.strip().encode("utf-8")).hexdigest()

def extract_years(cv_text):
    matches = re.findall(r'(\d{4})\s*[-–]\s*(\d{4}|Present)', cv_text)
    total = 0
    for start, end in matches:
        start = int(start)
        end = datetime.now().year if end.lower() == "present" else int(end)
        total += end - start
    return total

def detect_job_hopper(cv_text):
    matches = re.findall(r'(\d{4})\s*[-–]\s*(\d{4}|Present)', cv_text)
    return "Yes" if len(matches) >= 4 else "No"

def score_requirement(req, cv_text):
    if req.lower() in cv_text.lower():
        return 5, f"✅ Fully matched: candidate clearly meets '{req}'."
    else:
        words = req.lower().split()
        matches = sum(1 for w in words if w in cv_text.lower())
        score = round((matches / len(words)) * 5)
        if score < 1:
            score = 1
        reason = f"⚠️ Partial match: '{req}' only partially found in CV." if score < 5 else f"✅ Fully matched: '{req}'"
        return score, reason

def extract_name_contact(cv_text):
    lines = [l.strip() for l in cv_text.split("\n") if l.strip()]
    candidate_name = lines[0] if lines else "Unknown"

    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", cv_text)
    email = email_match.group(0) if email_match else "Not found"

    phone_match = re.search(r"\+?\d[\d\s\-]{7,}\d", cv_text)
    phone = phone_match.group(0) if phone_match else "Not found"

    candidate_contact = f"{email} | {phone}" if phone != "Not found" else email
    return candidate_name, candidate_contact

# ----- PAGE SELECTION -----
page = st.sidebar.radio("Select Page", ["CV Screening", "Search / Download"])

# ----- PAGE 1: CV SCREENING -----
if page == "CV Screening":
    st.title(APP_TITLE)
    st.subheader(SCREENING_SUBTITLE)

    st.text(REQUIREMENTS_LABEL)
    requirements = st.text_area(REQUIREMENTS_LABEL, height=200, placeholder="Example:\n- 2+ years in IT support\n- Experience with Microsoft 365")

    st.text(CV_LABEL)
    cv_text = st.text_area(CV_LABEL, height=400, placeholder="Paste the full resume/CV text here")

    if st.button("Screen CV"):
        if not requirements.strip() or not cv_text.strip():
            st.warning("⚠️ Please enter both requirements and candidate CV.")
        else:
            candidate_name, candidate_contact = extract_name_contact(cv_text)
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
            st.write(f"**Candidate Name:** {candidate_name}")
            st.write(f"**Candidate Contact:** {candidate_contact}")
            for r, reason in zip(results, reasoning):
                st.write(r)
                st.write(f"   - {reason}")

            st.write(f"\n**Job Hopper:** {job_hopper}")
            st.write(f"**Estimated Years of Experience:** {years_exp}")
            st.write(f"**Average Score:** {average_score}")
            st.write(f"**Overall Result:** {overall_result}")
            st.write(f"**Summary:** {summary}")

            # Save to DB if not duplicate
            db = load_db()
            cv_id = hash_cv(cv_text)
            if not any(c['id'] == cv_id for c in db):
                db.append({
                    "id": cv_id,
                    "name": candidate_name,
                    "contact": candidate_contact,
                    "cv_text": cv_text,
                    "requirements": requirements,
                    "results": results,
                    "reasoning": reasoning,
                    "job_hopper": job_hopper,
                    "years_exp": years_exp,
                    "average_score": average_score,
                    "overall_result": overall_result,
                    "summary": summary,
                    "date": str(datetime.now())
                })
                save_db(db)
                st.success("✅ Candidate saved successfully.")
            else:
                st.info("⚠️ Duplicate CV detected – not saved.")

# ----- PAGE 2: SEARCH / DOWNLOAD -----
elif page == "Search / Download":
    st.title(APP_TITLE)
    st.subheader(SEARCH_SUBTITLE)
    search_req = st.text_area("Enter keyword(s) to search in CVs", height=100)
    db = load_db()
    if st.button("Search"):
        if not search_req.strip():
            st.warning("⚠️ Enter keyword(s) to search.")
        else:
            filtered = []
            for c in db:
                if search_req.lower() in c['cv_text'].lower():
                    filtered.append(c)

            if not filtered:
                st.info("No candidates match your search.")
            else:
                st.subheader(f"{len(filtered)} Candidate(s) Found")
                for i, c in enumerate(filtered, 1):
                    st.write(f"{i}. {c['name']} – {c['contact']} – {c['overall_result']} – Avg: {c['average_score']}")
                    st.write(f"   Summary: {c['summary']}")

                # Download CSV
                df = pd.DataFrame([{
                    "Name": c['name'],
                    "Contact": c['contact'],
                    "Overall Result": c['overall_result'],
                    "Average Score": c['average_score'],
                    "Summary": c['summary']
                } for c in filtered])
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(DOWNLOAD_BUTTON_TEXT, csv, "shortlisted_candidates.csv", "text/csv")
