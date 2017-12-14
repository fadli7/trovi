from django.contrib import admin
from api import models as m

admin.site.register(m.Persona)
admin.site.register(m.Tag)
admin.site.register(m.Tutorial)
admin.site.register(m.Illustration)

# Register your models here.
