def screen_cv(requirements, cv_text):
    prompt = f"""
    You are an AI CV screener. Compare this candidate's CV against the job requirements.

    Job Requirements (Non-Negotiables):
    {requirements}

    Candidate CV:
    {cv_text}

    Task:
    - Decide if the candidate PASSES or FAILS.
    - If Pass, rate each requirement 1–5 and give a short reason.
    - Return results in this format:

    RESULT: PASS or FAIL
    SCORES:
    - Requirement 1: X/5
    - Requirement 2: X/5
    (etc.)
    SUMMARY: (one short paragraph why)
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # fast + smart
        messages=[{"role": "user", "content": prompt}],
    )
    
    return response.choices[0].message.content
