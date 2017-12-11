from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class IndexView(TemplateView):
    template_name = "staticweb/index.html"

class SignupView(TemplateView):
    template_name = "staticweb/signup.html"

class LoginView(TemplateView):
    template_name = "staticweb/login.html"

class ExploreView(TemplateView):
    template_name = "staticweb/explore.html"

class DashboardView(TemplateView):
    template_name = "staticweb/dashboard.html"

class PendingView(TemplateView):
    template_name = "staticweb/pending.html"

class PaymentView(TemplateView):
    template_name = "staticweb/payment.html"

class TutorView(TemplateView):
    template_name = "staticweb/tutor.html"

class cssView(TemplateView):
	template_name = "static/css"

class jsView(TemplateView):
	template_name = "static/js"