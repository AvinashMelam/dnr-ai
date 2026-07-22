from ai_engine.models import AIAnalysis


def execute_query(query):

    action = query.get("action")

    if action == "top_performer":

        top = (
            AIAnalysis.objects
            .select_related(
                "resume__student__user"
            )
            .order_by("-ats_score")
            .first()
        )

        if not top:
            return {}

        return {
            "name": top.resume.student.user.get_full_name()
                    or top.resume.student.user.username,
            "ats": top.ats_score,
            "branch": top.resume.student.branch
        }


    elif action == "average_ats":

        analyses = AIAnalysis.objects.all()

        if not analyses.exists():
            return {}

        avg = sum(a.ats_score for a in analyses) / analyses.count()

        return {
            "average_ats": round(avg,2)
        }


    return {}