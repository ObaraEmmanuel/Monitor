from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "biometric"

urlpatterns = [
    path('check/', views.check, name="check"),
    path('username/verify', views.verify_username, name="verify_username"),
    path('report/<int:duration>/<str:username>/', views.report, name="report"),
    path('emails/', views.send_mails, name="emails"),
]