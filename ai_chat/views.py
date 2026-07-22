from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json

from ai_engine.gemini import generate_sql, generate_chat_response
from ai_engine.sql_executor import execute_sql


def chat_page(request):
    return render(request, "ai_chat/chat.html")


@csrf_exempt
def ask_ai(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required."},
            status=405
        )

    try:

        data = json.loads(request.body)

        question = data.get("question", "").strip()

        if not question:
            return JsonResponse({
                "answer": "Please enter a question."
            })

        try:
            student_api_key = request.user.student_profile.gemini_api_key

            if not student_api_key:
                    return JsonResponse({
                        "answer": "No Gemini API key is configured for your account."
                    })

        except StudentProfile.DoesNotExist:
            return JsonResponse({
                "answer": "Student profile not found."
            })
    
        # ------------------------------------
        # STEP 1 : Generate SQL
        # ------------------------------------

        sql = generate_sql(
            question,
            student_api_key
        )

        if not sql:
            return JsonResponse({
                "answer": "The AI service is temporarily unavailable. Please try again in a few moments."
            })
        print("\nGenerated SQL:\n", sql)

        # ------------------------------------
        # STEP 2 : Execute SQL
        # ------------------------------------

        records = execute_sql(sql)

        print("\nQuery Result:\n", records)

        # ------------------------------------
        # STEP 3 : Ask Gemini to explain
        # ------------------------------------

        prompt = f"""
You are an AI Placement Officer.

Answer the user's question using ONLY the database results below.

User Question:
{question}

SQL Executed:
{sql}

Database Result:
{records}

Instructions:
- Be friendly.
- Do not invent information.
- If no records are found, clearly say so.
- Format the answer nicely.
"""

        answer = format_answer(records)

        return JsonResponse({

        "answer":answer

        })

    except Exception as e:

        print(e)

        return JsonResponse(
            {
                "error": str(e)
            },
            status=500
        )