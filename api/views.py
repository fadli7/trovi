from django.contrib.syndication.views import Feed
from django.http import JsonResponse, HttpResponseRedirect, QueryDict
from django.views import View
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Count
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.mail import send_mail
from django.urls import reverse

from api.forms import (UserUpdateForm, UserCreationForm, PasswordChangeForm, TransactionForm,
        PaginationForm, PersonaForm, EmailConfirmationForm, UserPictureUpdateForm)
from api.models import Tutorial, Persona
# Create your views here.

class LatestTuroialFeed(Feed):
    title = 'Latest tutorial of trovi'
    link = '/drtutorial/'
    description = 'this feed is about the latest and newest tutorial than we provide'

    def items(self):
        return Tutorial.objects.all().order_by('-pk')[:5]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return reverse('explore')

class RegistrationView(View):

    def send_confirmation_mail(self, recipent, key):
        head = 'Email Confirmation'
        body = 'please confirm your account, localhost:8000/api/emailconfirmation/?key=' + key
        send_mail(head, body, 'd4ita2016@gmail.com', [recipent])

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            self.send_confirmation_mail(user.email, user.emailconfirmation.key)
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed', 'errors': form.errors})

class EmailConfirmationView(View):

    def get(self, request, *args, **kwargs):
        form = EmailConfirmationForm(request.GET)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('login'))

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
            url = static('gambar/4.png')

        return JsonResponse({'id': user.id, 'username': user.username,
            'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email,
            'picture': url, 'description': persona.description})

    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            logout(request)
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed', 'errors': form.errors})

    def put(self, request, *args, **kwarggs):
        put = QueryDict(request.body)
        form = UserUpdateForm(put, instance=request.user)

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
                tutorials = tutorials.annotate(buyers_count=Count('transactions__user')).order_by('-buyers_count')
            else:
                tutorials = tutorials.order_by('?')

        ret =  tutorials.distinct()

        if ret.exists():
            return ret
        else:
            return None

    def paginate(self, request, tutorials):
        form = PaginationForm(request.GET)

        if not form.is_valid():
            raise ValidationError(form.errors, code='pagination_error')

        page, page_length = form.cleaned_data['page'], form.cleaned_data['page_length']
        tutorials = tutorials[(page - 1) * page_length:page * page_length]
        tags_set = [tutorial.tags.all() for tutorial in tutorials]

        return (tutorials, tags_set,)

    def clean_data(self, request, tutorials, tags_set):
        tutorials = list(tutorials)
        tags_set = list(tags_set)

        data = []
        for tutorial, tags in zip(tutorials, tags_set):
            datum = {'id': tutorial.id, 'name': tutorial.name,
                    'banner': tutorial.banner.url, 'price': tutorial.price,
                    'tags': [tag.name for tag in tags]}

            data.append(datum)

        return data

    def full_process_data(self, request, tutorials):
        tutorials = self.get_batch(request, tutorials)

        if tutorials is None:
            return 'no data'

        tutorials, tags_set = self.paginate(request, tutorials)
        data = self.clean_data(request, tutorials, tags_set)

        return data

class ExploreView(BaseBatchTutorialMixin, View):

    def get(self, request, *args, **kwargs):
        tutorials = Tutorial.objects.prefetch_related().all()
        if request.user.is_authenticated:
            tutorials = tutorials.exclude(transactions__user__pk=request.user.id)

        try:
            data = self.full_process_data(request, tutorials)
        except ValidationError as e:
            return JsonResponse({'status': 'failed', 'errors': str(e)})

        return JsonResponse({'status': 'success', 'data': data})

class PendingView(BaseBatchTutorialMixin, View):

    def get(self, request, *args, **kwargs):
        tutorials = Tutorial.objects.all().prefetch_related().filter(transactions__user__pk=request.user.id)
        tutorials = tutorials.filter(transactions__is_reviewed=False)

        data = self.full_process_data(request, tutorials)

        return JsonResponse({'status': 'success', 'data': data})

class TutorialOwnedView(BaseBatchTutorialMixin, View):

    def get(self, request, *args, **kwargs):
        tutorials = Tutorial.objects.all().prefetch_related().filter(transactions__user__pk=request.user.id)
        tutorials = tutorials.filter(transactions__is_reviewed=True)

        data = self.full_process_data(request, tutorials)

        return JsonResponse({'status': 'success', 'data': data})

class TutorialView(View):

    def get(self, request, *args, **kwargs):
        tutorial_id = request.GET.get('id')

        try:
            tutorial = Tutorial.objects.prefetch_related().get(pk=tutorial_id, transactions__user=request.user.id)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'failed', 'errors': 'tutorial not bought'})

        tags = list(tag.name for tag in tutorial.tags.all())
        illustrations = list({'url': illustration.url, 'description': illustration.description}\
                for illustration in tutorial.illustrations.all())

        data = {
                'id': tutorial_id, 'name': tutorial.name,
                'banner': tutorial.banner.url, 'video': tutorial.video.url,
                'description': tutorial.description, 'tags': tags,
                'illustrations': illustrations
                }

        return JsonResponse({'status': 'success', 'data': data})

class TransactionView(View):

    def post(self, request, *args, **kwargs):
        form = TransactionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(request.user)
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed', 'errors': form.errors})

class PersonaView(View):

    def post(self, request, *args, **kwargs):
        form = PersonaForm(request.POST, request.FILES, instance=request.user.persona)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'failed', 'errors': form.errors})
