from django.conf.urls import url
from django.urls import path
from django.contrib.auth.decorators import login_required
from staticweb import views as v

urlpatterns = [
        url(r'^$', v.IndexView.as_view(), name="index"),
        url(r'^signup/$', v.SignupView.as_view(), name="signup"),
        url(r'^login/$', v.LoginView.as_view(), name="login"),
        url(r'^explore/$', v.ExploreView.as_view(), name="explore"),
        url(r'^dashboard/$', login_required(v.DashboardView.as_view()), name="dashboard"),
        url(r'^pending/$', login_required(v.PendingView.as_view()), name="pending"),
        path('payment/<int:tutorial>/<int:price>', login_required(v.PaymentView.as_view()), name="payment"),
        path('tutor/<int:id>', login_required(v.TutorView.as_view()), name="tutor"),
        url(r'^css/$', v.cssView.as_view(), name="css"),
        url(r'^js/$', v.jsView.as_view(), name="js"),
        url(r'^own/$', v.OwnView.as_view(), name="own"),
        ]
