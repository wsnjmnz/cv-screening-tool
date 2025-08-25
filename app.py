import streamlit as st
import pandas as pd

# --- Database (temporary in memory, can be replaced with SQLite later) ---
if "cvs" not in st.session_state:
    st.session_state["cvs"] = []

# --- Sidebar Navigation ---
st.sidebar.title("CV Screening Tool")
page = st.sidebar.radio("Go to", ["Screening", "Search"])

# --- Page 1: Screening ---
if page == "Screening":
    st.title("CV Screening")

    st.subheader("Non-Negotiables")
    non_negos = st.text_area("Enter non-negotiable qualifications (comma separated):")

    st.subheader("Paste Candidate CV")
    cv_text = st.text_area("Paste CV text here")

    if st.button("Check CV"):
        non_nego_list = [n.strip().lower() for n in non_negos.split(",") if n.strip()]
        cv_lower = cv_text.lower()
        result = "PASS"
        missing = []

        for n in non_nego_list:
            if n not in cv_lower:
                result = "FAIL"
                missing.append(n)

        if result == "PASS":
            st.success("Result: PASS ✅ All requirements found.")
        else:
            st.error(f"Result: FAIL ❌ Missing: {', '.join(missing)}")

        # Save candidate in "database"
        st.session_state["cvs"].append({
            "non_negos": non_nego_list,
            "cv_text": cv_text,
            "result": result
        })

# --- Page 2: Search ---
elif page == "Search":
    st.title("Search Candidates")

    st.subheader("Enter filter non-negotiables")
    search_non_negos = st.text_area("Enter search keywords (comma separated):")
    search_list = [s.strip().lower() for s in search_non_negos.split(",") if s.strip()]

    if st.button("Search"):
        results = []
        for i, cv in enumerate(st.session_state["cvs"]):
            if all(s in cv["cv_text"].lower() for s in search_list):
                results.append({"CV #": i+1, "Result": cv["result"], "CV Text": cv["cv_text"][:200] + "..."})

        if results:
            df = pd.DataFrame(results)
            st.dataframe(df)

            # Download button
            csv = pd.DataFrame(results).to_csv(index=False).encode("utf-8")
            st.download_button("Download Results", data=csv, file_name="shortlisted_candidates.csv", mime="text/csv")
        else:
            st.warning("No candidates found.")
