import streamlit as st
from openai import OpenAI
import os

# Load OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("AI CV Screener")

# Input fields
non_nego = st.text_area("Enter Non-Negotiable Requirements (one per line)")
cv_text = st.text_area("Paste Candidate CV")

if st.button("Screen CV"):
    if not non_nego or not cv_text:
        st.warning("Please enter both requirements and CV.")
    else:
        with st.spinner("Screening..."):
            prompt = f"""
You are an AI CV screener. Compare the CV below to the job requirements.

Requirements:
{non_nego}

Candidate CV:
{cv_text}

Respond with:
- PASS or FAIL
- Short reasoning why.
"""
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content
            st.success(result)
