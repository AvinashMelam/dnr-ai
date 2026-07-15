from ai_engine.prompts import RESUME_ANALYSIS_PROMPT

import json

from google import genai
# from dotenv import load_dotenv

from ai_engine.prompts import RESUME_ANALYSIS_PROMPT


def generate_resume_analysis(resume_text, student_api_key,job_description="" ):

    client = genai.Client(api_key=student_api_key)

    prompt = f"""
    {RESUME_ANALYSIS_PROMPT}

    Resume

    {resume_text}

    Job Description

    {job_description}
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        return json.loads(response.text)
    except Exception as e:
        error = str(e)
        print("Gemini Error:", error)
        return {
            "error": error
        }