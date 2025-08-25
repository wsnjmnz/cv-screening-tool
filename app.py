import streamlit as st

st.set_page_config(page_title="AI CV Screener", layout="wide")

st.title("📄 AI CV Screener (Free / Local Version)")

# Input boxes
st.subheader("Enter Non-Negotiable Requirements (one per line)")
requirements = st.text_area("Requirements", height=200, placeholder="Example:\n- 2+ years in IT support\n- Experience with Microsoft 365\n- Strong communication skills")

st.subheader("Paste Candidate CV")
cv_text = st.text_area("Candidate CV", height=400, placeholder="Paste the full resume/CV text here")

# Simple matching logic
if st.button("Screen CV"):
    if not requirements.strip() or not cv_text.strip():
        st.warning("⚠️ Please enter both requirements and a candidate CV.")
    else:
        reqs = [r.strip() for r in requirements.split("\n") if r.strip()]
        results = []
        score = 0

        for req in reqs:
            if req.lower() in cv_text.lower():
                results.append(f"✅ {req}")
                score += 1
            else:
                results.append(f"❌ {req}")

        st.subheader("Results")
        st.write("\n".join(results))
        st.write(f"**Match Score:** {score}/{len(reqs)}")
        
        if score == len(reqs):
            st.success("🎉 Candidate meets all requirements!")
        else:
            st.error("❌ Candidate does not meet all requirements.")
