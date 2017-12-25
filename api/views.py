from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Count
from django.contrib.auth.models import User

from api.forms import UserUpdateForm, UserCreationForm, PasswordChangeForm, PaymentForm, PaginationForm
from api.models import Tutorial
from api.mixins import BaseBatchTutorialMixin
# Create your views here.

class RegistrationView(View):

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed', 'errors': form.errors})

class AuthView(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse({'logged_in': request.user.is_authenticated})

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed'})

    def delete(self, request, *args, **kwargs):
        logout(request)
        return JsonResponse({'status': 'success'})

class UserView(View):

    def get(self, request, *args, **kwargs):
        user = request.user
        persona = user.persona

        if persona.picture:
            url = persona.picture.url
        else:
            url = static('1.jpg')

        return JsonResponse({'id': user.id, 'username': user.username,
            'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email,
            'picture': url, 'description': persona.description})

    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(request.POST, instance=request.user)

        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, username=request.user.username, password=data['password'])
            if user is not None:
                form.save()
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed', 'errors': form.errors})

    def put(self, request, *args, **kwarggs):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed', 'errors': form.errors})


class ExploreView(BaseBatchTutorialMixin, View):

    def get(self, request, *args, **kwargs):
        tutorials = Tutorial.objects.all()
        if request.user.is_authenticated:
            tutorials = tutorials.exclude(buyers__pk=request.user.id)

        data = self.full_process_data(request, tutorials)

        return JsonResponse({'status': 'success', 'data': data})

class PendingView(BaseBatchTutorialMixin, View):

    def get(self, request, *args, **kwargs):
        tutorials = Tutorial.objects.all().filter(transaction__user__pk=rquest.user.id)
        tutorials = tutorials.filter(transaction__is_reviewed=False)

        data = self.full_process_data(request, tutorials)

        return JsonResponse({'status': 'success', 'data': data})

class TutorialOwnedView(View):

    def get(self, request, *args, **kwargs):
        tutorials = Tutorial.objects.all().filter(transaction__user__pk=request.user.id)
        tutorials = tutorials.filter(transaction__is_reviewed=True)

        data = self.full_process_data(request, tutorials)

        return JsonResponse({'status': 'success', 'data': data})

class TutorialView(View):

    def get(self, request, *args, **kwargs):
        tutorial_id = request.GET.get('id')
        tutorial = Tutorial.objects.prefetch_related().filter(pk=tutorial_id).first()
        tags = list(tag.name for tag in tutorial.tags.all())
        illustrations = list(illustration.url for illustration in tutorial.illustration_set.all())

        data = {
                'id': tutorial_id, 'name': tutorial.name,
                'banner': tutorial.banner.url, 'video': tutorial.video.url,
                'description': tutorial.description, 'tags': tags,
                'illustrations': illustrations
                }

        return JsonResponse({'status': 'success', 'data': data})

class TransactionView(View):

    def post(self, request, *args, **kwargs):
        form = PaymentForm(request.POST)
        if form.is_valid:
            form.save()
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed', 'errors': form.errors})

