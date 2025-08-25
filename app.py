import streamlit as st
from huggingface_hub import InferenceClient

# Load Hugging Face model (free)
client = InferenceClient("mistralai/Mistral-7B-Instruct-v0.2")

st.title("AI CV Screening Tool (Free Version)")

# Upload CV
uploaded_file = st.file_uploader("Upload CV (PDF or TXT)", type=["pdf", "txt"])

# Job description input
job_description = st.text_area("Paste Job Description")

if uploaded_file and job_description:
    # Read CV text
    if uploaded_file.type == "application/pdf":
        import fitz  # PyMuPDF for PDF parsing
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        cv_text = ""
        for page in doc:
            cv_text += page.get_text()
    else:
        cv_text = uploaded_file.read().decode("utf-8")

    # Build prompt
    prompt = f"""
    You are an AI CV screener. 
    Evaluate the following CV against this job description.

    Job Description:
    {job_description}

    CV:
    {cv_text}

    Provide a score from 1–5 and explain briefly why.
    """

    # Call Hugging Face model
    with st.spinner("Screening CV..."):
        response = client.text_generation(prompt, max_new_tokens=500)

    # Display result
    st.subheader("Screening Result")
    st.write(response)
