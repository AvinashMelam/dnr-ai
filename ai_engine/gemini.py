import json

from ai_engine.schema import get_database_schema
from ai_engine.prompts import SQL_PROMPT
from google import genai
# from dotenv import load_dotenv
import time

from ai_engine.prompts import RESUME_ANALYSIS_PROMPT

def get_client(api_key):
    return genai.Client(api_key=api_key)

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

def generate_sql(question, api_key):

    client = get_client(api_key)

    schema = get_database_schema()
    prompt = f"""
    {schema}
    {SQL_PROMPT}
    Question:

    {question}
    """

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )

            return response.text.strip()

        except Exception as e:

            print("SQL Generation Error:", e)
            time.sleep(2)
    return None
    
def generate_chat_response(prompt, student_api_key):

    client = get_client(student_api_key)

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:

        print("Gemini Error:", e)

        return "Sorry, I couldn't process your request."