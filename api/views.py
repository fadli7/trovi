from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from django.contrib.auth import authenticate

# Create your views here.

class LoginView(View):

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({status: 'success'})

        return JsonResponse({status: 'failed'})
