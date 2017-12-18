from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views import View
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout

from api.forms import UserUpdateForm, UserCreationForm, PasswordChangeForm, PaymentForm, PageForm
from api.models import Tutorial
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
        # return JsonResponse(request.POST)
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
        return JsonResponse({'id': user.id, 'username': user.username,
            'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email
            'image': persona.image.url, 'description': persona.description})

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

class PageView(View):

    def get(self, request, *args, **kwargs):
        form = PageView(request.GET)

        if not form.is_valid:
            return JsonResponse({'status': 'failed', 'errors': form.errors})

        page = form.cleaned_data['page']
        page_length = form.cleaned_data['page_length']

        tutorials = Tutorial.objects.all()

        if request.user.is_authenticated:
            tutorials = tutorials.exclude(buyers__id=request.user.id)

        if 'tags' in request.GET:
            tags = request.GET.get('tags').split(',')
            tutorials = tutorials.filter(tags__in=tags)

        if 'q' in request.GET:
            q = request.GET.get('q')
            regex_q = r'(' + q.replace(',', '|') + r')'
            tutorials = tutorials.filter(name__iregex=regex_q)

        data = [tutorials[(page - 1) * page_length:page * page_length]]
        return JsonResponse({'status': 'success', 'data': data})

class TransactionView(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse({'status': 'success'})

    def post(self, request, *args, **kwargs):
        form = PaymentForm(request.POST)
        if form.is_valid:
            form.save()
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed', 'errors': form.errors})

