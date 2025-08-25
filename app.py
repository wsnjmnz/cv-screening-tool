import streamlit as st

st.set_page_config(page_title="AI-style CV Screener", layout="wide")

st.title("📄 AI-Style CV Screener (Text-Based)")

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

# Screening logic
if st.button("Screen CV"):
    if not requirements.strip() or not cv_text.strip():
        st.warning("⚠️ Please enter both requirements and a candidate CV.")
    else:
        reqs = [r.strip() for r in requirements.split("\n") if r.strip()]
        results = []
        total_score = 0

        for req in reqs:
            # Simple keyword check
            if req.lower() in cv_text.lower():
                score = 5
            else:
                # Partial match based on words
                words = req.lower().split()
                matches = sum(1 for w in words if w in cv_text.lower())
                score = round((matches / len(words)) * 5)
                if score < 1:
                    score = 1
            results.append(f"{req} – {score}")
            total_score += score

        average_score = round(total_score / len(reqs), 2)
        pass_fail = "PASS" if average_score >= 4 else "FAIL"

        # Display results
        st.subheader("Screening Results")
        for r in results:
            st.write(r)
        st.write(f"\n**✅ Result:** {average_score} Average – {pass_fail}")
