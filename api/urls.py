from django.contrib.auth.decorators import login_required

from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from api.views import AuthView, RegistrationView, UserView, ExploreView, TutorialView, TutorialOwnedView, PendingView, TransactionView

urlpatterns = [
        url(r'^auth/$', AuthView.as_view()),
        url(r'^registration/$', RegistrationView.as_view()),
        url(r'^user/$', login_required(UserView.as_view())),
        url(r'^explore/$', ExploreView.as_view()),
        url(r'^tutorial/$', login_required(TutorialView.as_view())),
        url(r'^owned/$', login_required(TutorialOwnedView.as_view())),
        url(r'^pending/$', login_required(PnedingView.as_view())),
        url(r'^transaction/$', login_required(TransactionView.as_view())),
        ]
