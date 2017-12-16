from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views import View
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

from api.forms import UserUpdateForm
from api.models import Tutorial
# Create your views here.

class RegistrationView(View):

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed'})

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
        return JsonResponse({'id': user.id, 'username': user.username,
            'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email})

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        user = authenticate(request, username=username, password=password)
        if user == request.user and password1 == password2:
            user.set_password(password1)
            user.save()
            logout(request)
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed'})

    def put(self, request, *args, **kwarggs):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed'})

class PageView:

    def get(self, request, *args, **kwargs):
        page = int(request.GET.get('page'))
        page_lenth = int(request.Get.get('page_length'))

        tutorials = Tutorial.objects

        if request.user.is_authenticated:
            tutorials = tutorials.exclude(buyers__id=request.user.id)

        if 'tags' in request.GET:
            tags = request.GET.get('tags').split(' ')
            tutorials = tutorials.filter(tags__in=tags)

        if 'q' in request.GET:
            q = request.GET.get('q')
            regex_q = r'*(' + q.replace(' ', '|') + r')*'
            tutorials = tutorials.filter(name__iregex=regex_q)

        paginator = Paginator(tutorials)
        data = paginator.page(page)
        return JsonResponse({'status': 'success', 'data': data})

