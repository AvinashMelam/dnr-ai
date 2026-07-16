from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from students.models import StudentProfile, Resume
from students.utils import extract_resume_text
from ai_engine.models import AIAnalysis
from ai_engine.parser import parse_analysis
from ai_engine.gemini import generate_resume_analysis
from django.db.models import Avg, Count
from google import genai
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from google.genai import types

from google.genai.errors import APIError

# -------------------------
# Core
# -------------------------

def home(request):
    return render(request, 'core/home.html')


# -------------------------
# Authentication
# -------------------------

def register(request):
    if request.method == "POST":

            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, "accounts/register.html")
            # Validation
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return render(request, "accounts/register.html")

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return render(request, "accounts/register.html")

            # Create User
            User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            messages.success(request, "Registration Successful. Please Login.")

            return redirect("login")

    return render(request, "accounts/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        User = authenticate(request, username=username, password=password)

        if User is not None:
            login(request, User)
            messages.success(request, "Login Successful.")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid Credentials.")
        
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "Logout Successful")

    return redirect("login")

# -------------------------
# Student
# -------------------------

@login_required(login_url='login')
def dashboard(request):
    profile = get_object_or_404(
            StudentProfile,
            user=request.user
        )

    latest_resume = Resume.objects.filter(
        student=profile
    ).order_by("-uploaded_at").first()

    analysis = None

    if latest_resume and latest_resume.analysis_status == "Completed":

        analysis = AIAnalysis.objects.filter(
            resume=latest_resume
        ).first()

    recent_resumes = Resume.objects.filter(
        student=profile
    ).order_by("-uploaded_at")

    context = {

        "profile": profile,

        "resume": latest_resume,

        "analysis": analysis,
        
        "recent_resumes": recent_resumes,

    }

    print(context)

    return render(
        request,
        "students/dashboard.html",
        context
    )

@login_required(login_url='login')
def profile(request):
    # Get profile if exists, otherwise create one
    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )
    if request.method == "POST":

        profile.college_name = request.POST.get("college_name")
        profile.branch = request.POST.get("branch")
        profile.gemini_api_key = request.POST.get("gemini_api_key")

        year = request.POST.get("year")
        profile.year = int(year) if year else None

        profile.career_goal = request.POST.get("career_goal")
        profile.github = request.POST.get("github")
        profile.linkedin = request.POST.get("linkedin")
        profile.portfolio = request.POST.get("portfolio")
        profile.about_me = request.POST.get("about_me")

        profile.save()

        messages.success(
            request,
            "✅ Profile updated successfully! Now upload your resume to start AI analysis."
        )

        return redirect("resume_upload")
    
    context = {
        "profile": profile
    }

    return render(request, 'students/profile.html', context)

@login_required(login_url='login')
def edit_profile(request):
    return render(request, 'students/profile.html')



@login_required(login_url="login")
def resume_upload(request):

    # Get logged-in student's profile
    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        resume_file = request.FILES.get("resume_file")
        job_description = request.POST.get("job_description")

        # Save Resume
        Resume.objects.create(
            student=profile,
            resume_file=resume_file,
            job_description=job_description,
            analysis_status="Uploaded"
        )

        messages.success(
            request,
            "Resume uploaded successfully."
        )

        return redirect("/resume/history/")


    return render(request, "students/resume_upload.html")
    
@login_required(login_url='login')
def resume_history(request):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    resumes = Resume.objects.filter(
        student=profile
    ).order_by("-uploaded_at")

    context = {
        "resumes": resumes
    }

    return render(request, "students/history.html", context)


# The Process of analysis takes place here
@login_required(login_url="login")
def analyze_resume(request, resume_id):

    profile = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    resume = get_object_or_404(
        Resume,
        id=resume_id,
        student=profile
    )

    # Extract PDF Text
    extracted_text = extract_resume_text(
        resume.resume_file.path
    )

    # Save into database
    resume.resume_text = extracted_text
    resume.analysis_status = "Text Extracted"
    resume.save()

    # -------------------------------
    # Check Gemini API Key
    # -------------------------------

    student_key = resume.student.gemini_api_key

    if not student_key:

        messages.error(
            request,
            "Please add your Gemini API Key in your profile before using AI Analysis."
        )

        return redirect("profile")   # <-- change to your profile URL name

    # -------------------------------
    # Gemini Analysis
    # -------------------------------

    try:
        response = generate_resume_analysis(
            extracted_text,
            resume.student.gemini_api_key,
            resume.job_description
        )
        if response is None:

            messages.error(
                request,
                "AI could not generate analysis. Please check your Gemini API Key or try again."
            )

            return redirect("resume_history")

    except Exception as e:
        messages.error(
            request,
            f"AI Analysis Failed: {e}"
        )

    try:
        if "error" in response:
            if "503" in response["error"]:

                messages.error(
                    request,
                    "🤖 Gemini AI is currently experiencing high demand. Please try again after a few minutes."
                )

            elif "401" in response["error"]:

                messages.error(
                    request,
                    "❌ Invalid Gemini API Key."
                )

            elif "429" in response["error"]:

                messages.error(
                    request,
                    "⚠ Gemini API quota exceeded."
                )

            else:

                messages.error(
                    request,
                    response["error"]
                )

            return redirect("resume_history")

        # ===============================
        # Parse AI Response
        # ===============================            
        data = parse_analysis(response)
    except Exception as e:
        messages.error(request, f"Parser Error: {e}")
        return redirect("resume_history")

    AIAnalysis.objects.update_or_create(
    resume=resume,
    defaults=data
    )

    resume.analysis_status = "Completed"
    resume.save()

    return redirect("analysis", resume.id)

# May be will return the analysed result
@login_required(login_url='login')
def analysis(request, resume_id):
    profile = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    resume = get_object_or_404(
        Resume,
        id=resume_id,
        student=profile
    )

    analysis = get_object_or_404(
        AIAnalysis,
        resume=resume
    )

    context = {
        "resume": resume,
        "analysis": analysis,
    }

    return render(
        request,
        "students/analysis.html",
        context
    )

@login_required(login_url='login')
def analysis_history(request):
    return render(request, 'students/history.html')

@login_required(login_url='login')
def feedback(request):
    return render(request, 'students/feedback.html')


# -------------------------
# Admin
# -------------------------

def admin_dashboard(request):
    total_students = StudentProfile.objects.count()

    total_resumes = Resume.objects.count()

    total_analysis = AIAnalysis.objects.count()

    avg_ats = AIAnalysis.objects.aggregate(
        Avg("ats_score")
    )["ats_score__avg"] or 0

    avg_technical = AIAnalysis.objects.aggregate(
        Avg("technical_score")
    )["technical_score__avg"] or 0

    avg_job_match = AIAnalysis.objects.aggregate(
        Avg("job_match_score")
    )["job_match_score__avg"] or 0

    avg_interview = AIAnalysis.objects.aggregate(
        Avg("interview_readiness_score")
    )["interview_readiness_score__avg"] or 0

    # Resume Quality Analytics

    excellent = AIAnalysis.objects.filter(
        resume_quality="Excellent"
    ).count()

    good = AIAnalysis.objects.filter(
        resume_quality="Good"
    ).count()

    average = AIAnalysis.objects.filter(
        resume_quality="Average"
    ).count()

    poor = AIAnalysis.objects.filter(
        resume_quality="Poor"
    ).count()

    total_quality = excellent + good + average + poor

    if total_quality > 0:
        excellent_percent = round((excellent / total_quality) * 100)
        good_percent = round((good / total_quality) * 100)
        average_percent = round((average / total_quality) * 100)
        poor_percent = round((poor / total_quality) * 100)
    else:
        excellent_percent = 0
        good_percent = 0
        average_percent = 0
        poor_percent = 0

    # Branch-wise Students

    branch_stats = StudentProfile.objects.values(
    "branch"
    ).annotate(
        total=Count("id")
    ).order_by("-total")

    # Branch-wise ATS
    branch_ats = AIAnalysis.objects.values(
    "resume__student__branch"
    ).annotate(
        avg_ats=Avg("ats_score")
    ).order_by("-avg_ats")

    branch_ats_labels = [
        i["resume__student__branch"]
        for i in branch_ats
    ]

    branch_ats_data = [
        round(i["avg_ats"])
        for i in branch_ats
    ]

    # Top Performers

    top_students = AIAnalysis.objects.select_related(
    "resume",
    "resume__student",
    "resume__student__user"
    ).order_by("-overall_score")[:10]

    print("top_students")
    print(top_students)
    # Students Without Resume
    students_without_resume = StudentProfile.objects.filter(
    resumes__isnull=True
    ).count()

    # Interview Readiness
    ready = AIAnalysis.objects.filter(
    interview_readiness_score__gte=80
    ).count()

    almost_ready = AIAnalysis.objects.filter(
        interview_readiness_score__range=(60,79)
    ).count()

    needs_improvement = AIAnalysis.objects.filter(
        interview_readiness_score__lt=60
    ).count()

    # Branch Performance Leaderboard

    branch_performance = AIAnalysis.objects.values(
        "resume__student__branch"
    ).annotate(
        avg_ats=Avg("ats_score"),
        avg_technical=Avg("technical_score"),
        avg_job=Avg("job_match_score"),
        avg_interview=Avg("interview_readiness_score")
    ).order_by("-avg_ats")


    # Interview readyness

    total_interview = ready + almost_ready + needs_improvement

    if total_interview > 0:
        interview_percentage = round(
            (
                ready * 100 +
                almost_ready * 70 +
                needs_improvement * 30
            ) / total_interview
        )
    else:
        interview_percentage = 0



    quality_labels = [
    "Excellent",
    "Good",
    "Average",
    "Poor"
    ]

    quality_data = [
        excellent,
        good,
        average,
        poor
    ]

    # Pass Context

    context = {

        "total_students": total_students,
        "total_resumes": total_resumes,
        "total_analysis": total_analysis,

        "avg_ats": round(avg_ats),
        "avg_technical": round(avg_technical),
        "avg_job_match": round(avg_job_match),
        "avg_interview": round(avg_interview),

        "branch_stats": branch_stats,
        "branch_ats": branch_ats,

        "excellent": excellent,
        "good": good,
        "average": average,
        "poor": poor,

        "excellent_percent": excellent_percent,
        "good_percent": good_percent,
        "average_percent": average_percent,
        "poor_percent": poor_percent,

        "ready": ready,
        "almost_ready": almost_ready,
        "needs_improvement": needs_improvement,

        "top_students": top_students,

        "students_without_resume": students_without_resume,
    }
        # For Charts
    context["branch_labels"] = [
    i["branch"] for i in branch_stats
    ]

    context["branch_data"] = [
    i["total"] for i in branch_stats
    ]

    branch_labels = [b["branch"] for b in branch_stats]
    branch_data = [b["total"] for b in branch_stats]

    context["branch_labels"] = branch_labels
    context["branch_data"] = branch_data

    context["quality_labels"] = quality_labels
    context["quality_data"] = quality_data

    context["branch_ats_labels"] = branch_ats_labels
    context["branch_ats_data"] = branch_ats_data

    context["interview_percentage"] = interview_percentage

    context["branch_performance"] = branch_performance


    return render(request, 'management/admin_dashboard.html', context)


# -------------------------
# API Checking
# -------------------------


# @require_POST
# @login_required(login_url="login")
# def test_api_key(request):

#     api_key = request.POST.get("api_key")

#     try:

#         client = genai.Client(
#             api_key=api_key
#         )

#         client.models.generate_content(
#             model="gemini-2.5-flash",
#             contents="Hello"
#         )

#         return JsonResponse({

#             "status": "success"

#         })

#     except Exception:

#         return JsonResponse({

#             "status": "failed"

#         })


# -------------------------
# Error Pages
# -------------------------

def page_not_found(request, exception):
    return render(request, 'core/404.html', status=404)

# Checking api key

def test_api_key(request):
    if request.method == "POST":
        api_key = request.POST.get("api_key", "").strip()
        
        if not api_key:
            return JsonResponse({
                "status": "error", 
                "message": "API key input is empty."
            })

        try:
            # 1. Initialize client
            client = genai.Client(api_key=api_key)
            
            # 2. Try the primary model
            try:
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents='test'
                )
            except APIError as e:
                # If overloaded, try the high-availability model
                if "demand" in str(e).lower() or e.code == 503:
                    response = client.models.generate_content(
                        model='gemini-3.1-flash-lite',
                        contents='test'
                    )
                else:
                    # Otherwise, bubble up other errors (like invalid API keys)
                    raise e
            
            # SUCCESS PATH: If either model call succeeds, return success to the JS
            return JsonResponse({"status": "success"})
            
        except APIError as e:
            # Capture specific Google validation/authentication issues
            return JsonResponse({
                "status": "error", 
                "message": f"Google API Error: {e.message}"
            })
        except Exception as e:
            # Capture network or system bugs
            return JsonResponse({
                "status": "error", 
                "message": f"Server Error: {str(e)}"
            })

    # Reject non-POST requests
    return JsonResponse({"status": "error", "message": "Invalid request method."})