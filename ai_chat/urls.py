from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_page, name="ai_chat"),
    path("ask/", views.ask_ai, name="ask_ai"),
]