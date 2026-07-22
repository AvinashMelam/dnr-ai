"""
URL configuration for myproj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Public Pages
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Student
    path('dashboard/', views.dashboard, name='dashboard'),

    # Student Profile
    path('profile/', views.profile, name='profile'),
    
    # Resume
    path('resume/upload/', views.resume_upload, name='resume_upload'),
    path('resume/history/', views.resume_history, name='resume_history'),

    path("resume/analyze/<int:resume_id>/", views.analyze_resume, name="analyze_resume"),

    # AI Analysis
    path('analysis/<int:resume_id>/', views.analysis, name='analysis'),
    path('analysis/history/', views.analysis_history, name='analysis_history'),

    # API
    path("test-api-key/", views.test_api_key, name="test_api_key"),


    # Check API key
    path('test-api-key/', views.test_api_key, name='test_api_key'),

    #  AI Chat
    path("ai-chat/", include("ai_chat.urls")),

    # Admin API Keys
    path("students/admin/api-keys/",views.api_keys,name="api_keys"),

    # Management Dashboard
    path('management/admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
] + static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)