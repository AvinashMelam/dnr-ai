# strengths = "\n".join(response["strengths"])

def parse_analysis(response):
    """
    Convert Gemini JSON response into
    Django model compatible dictionary.
    """

    return {

        "overall_score": response.get("overall_score", 0),

        "technical_score": response.get("technical_score", 0),

        "ats_score": response.get("ats_score", 0),

        "resume_quality": response.get("resume_quality", ""),

        "resume_summary": response.get("resume_summary", ""),

        "strengths": "\n".join(
            response.get("strengths", [])
        ),

        "weaknesses": "\n".join(
            response.get("weaknesses", [])
        ),

        "found_skills":"\n".join(
            response.get("found_skills", [])
        ),

        "missing_skills": "\n".join(
            response.get("missing_skills", [])
        ),

        "learning_priority": "\n".join(
            response.get("learning_priority", [])
        ),

        "job_roles": "\n".join(
            response.get("job_roles", [])
        ),

        "improvement_tips": "\n".join(
            response.get("improvement_tips", [])
        ),

        "interview_readiness_score": response.get(
            "interview_readiness_score",
            0
        )
    }