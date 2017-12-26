from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Count
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from api.forms import UserUpdateForm, UserCreationForm, PasswordChangeForm, TransactionForm, PaginationForm, PersonaForm
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

class BaseBatchTutorialMixin:

    def get_batch(self, request, tutorials):
        if 'tags' in request.GET:
            tags = request.GET.get('tags').split(' ')
            tutorials = tutorials.filter(tags__name__in=tags)

        if 'q' in request.GET:
            q = request.GET.get('q')
            regex_q = r'(' + q.replace(' ', '|') + r')'
            tutorials = tutorials.filter(name__iregex=regex_q)

        if 'ordering' in request.GET:
            ordering = request.GET.get('ordering')
            if ordering == 'new':
                tutorials = tutorials.order_by('-pk')
            elif ordering == 'popular':
                tutorials = tutorials.annotate(buyers_count=Count('buyers')).order_by('-buyers_count')
            else:
                tutorials = tutorials.order_by('?')

        return tutorials.distinct()

    def paginate(self, request, tutorials):
        form = PaginationForm(request.GET)

        if not form.is_valid():
            raise ValidationError(form.errors, code='pagination_error')

        page, page_length = form.cleaned_data['page'], form.cleaned_data['page_length']
        tutorials = tutorials[(page - 1) * page_length:page * page_length]
        tags = tutorials.tags

        print('------------------------------------------------------------------')
        print(tutorials, tags)
        return (tutorials, tags,)

    def clean_data(self, request, tutorials, tags):
        tutorials = list(tutorial)
        tags_set = list(tags.all())

        data = []
        for i in len(tutorials):
            tutorial, tags = tutorials[i], tags_set[i]
            datum = {'id': tutorial.id, 'name': tutorial.name,
                    'banner': tutorial.banner.url, 'price': tutorial.price,
                    'tags': [tag.name for tag in tags]}

            data.append(datum)

        return data

    def full_process_data(self, request, tutorials):
        tutorials = self.get_batch(request, tutorials)
        tutorials, tags = self.paginate(request, tutorials)
        data = self.clean_data(request, tutorials, tags)

        return data

class ExploreView(BaseBatchTutorialMixin, View):

    def get(self, request, *args, **kwargs):
        tutorials = Tutorial.objects.all()
        if request.user.is_authenticated:
            tutorials = tutorials.exclude(transaction__user__pk=request.user.id)

        try:
            data = self.full_process_data(request, tutorials)
        except ValidationError as e:
            return JsonResponse({'status': 'failed', 'errors': str(e)})

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
        form = TransactionForm(request.POST, request.FILE)
        if form.is_valid:
            form.save(request.user)
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed', 'errors': form.errors})

class PersonaView(View):

    def post(self, request, *args, **kwargs):
        form = PersonaForm(request.POST, request,FILE, instance=request.user.persona)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed', 'errors': form.errors})
