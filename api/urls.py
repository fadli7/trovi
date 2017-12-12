from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from api import views as v

urlpatterns = [
        url(r'auth', v.AuthView.as_view())
        ]
