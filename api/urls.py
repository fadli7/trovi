from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from api.views import Authview, RegistrationView, Authview

urlpatterns = [
        url(r'auth', AuthView.as_view()),
        url(r'user', UserView.as_view()),
        url(r'registration', RegistrationView.as_view()
        ]
