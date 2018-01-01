from django.contrib.auth.decorators import login_required

from django.urls import path
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from api import views
from django.views.generic.base import RedirectView

urlpatterns = [
        path('auth/', views.AuthView.as_view()),
        path('registration/', views.RegistrationView.as_view()),
        path('user/', login_required(views.UserView.as_view())),
        path('explore/', views.ExploreView.as_view()),
        path('tutorial/', login_required(views.TutorialView.as_view())),
        path('owned/', login_required(views.TutorialOwnedView.as_view())),
        path('pending/', login_required(views.PendingView.as_view())),
        path('transaction/', login_required(views.TransactionView.as_view())),
        path('emailconfirmation/', views.EmailConfirmationView.as_view()),
        path('feed/', views.LatestTuroialFeed()),
        url(r'^favicon\.ico$', RedirectView.as_view(url='/static/gambar/logo.png', permanent=True))
        ]
