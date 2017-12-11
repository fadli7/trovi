from django.conf.urls import url
from django.contrib.auth.decorators import login_required
import .views as v

urlpatterns = [
        url(r'^$', login_required(v.IndexView.as_view()), name="index"),
        url(r'^signup/$', login_required(v.SignupView.as_view()), name="signup"),
        url(r'^login/$', login_required(v.LoginView.as_view()), name="login"),
        url(r'^explore/$', login_required(v.ExploreView.as_view()), name="explore"),
        url(r'^dashboard/$', login_required(v.DashboardView.as_view()), name="dashboard"),
        url(r'^pending/$', login_required(v.PendingView.as_view()), name="pending"),
        url(r'^payment/$', login_required(v.PaymentView.as_view()), name="payment"),
        url(r'^tutor$', login_required(v.TutorView.as_view()), name="tutor"),
        ]
