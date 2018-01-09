from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from api.models import User, Persona, Tag, Tutorial, Illustration

admin.site.register(Persona)
admin.site.register(Tag)
admin.site.register(Tutorial)
admin.site.register(Illustration)
admin.site.register(User, UserAdmin)

# Register your models here.
