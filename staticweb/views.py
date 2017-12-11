from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class IndexView(TemplateView):
    template_name = "index.html"

class SignupView(TemplateView):
    template_name = "signup.html"

class LoginView(TemplateView):
    template_name = "login.html"

class ExploreView(TemplateView):
    template_name = "explore.html"

class DashboardView(TemplateView):
    template_name = "dashboard.html"

class PendingView(TemplateView):
    template_name = "pending.html"

class PaymentView(TemplateView):
    template_name = "payment.html"

class TutorView(TemplateView):
    template_name = "tutor.html"
