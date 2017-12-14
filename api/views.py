from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

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

    @login_required
    def get(self, request, *args, **kwargs):
        user = request.user
        return JsonResponse({'id': user.id, 'username': user.username,
            'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email})

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed'})
