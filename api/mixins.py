from api.forms import PaginationForm

class BaseBatchTutorialMixin:

    def get_batch(self, request, tutorials):
        if 'tags' in request.GET:
            tags = request.GET.get('tags').split(',')
            tutorials = tutorials.filter(tags__name__in=tags)

        if 'q' in request.GET:
            q = request.GET.get('q')
            regex_q = r'(' + q.replace(',', '|') + r')'
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
            return JsonResponse({'status': 'failed', 'errors': form.errors})

        page, page_length = form.cleaned_data['page'], form.cleaned_data['page_length']
        tutorials = tutorials[(page - 1) * page_length:page * page_length]
        tags = tutorials.tags

        return tutorials, tags

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

