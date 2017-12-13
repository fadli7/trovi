import uuid
import os
from django.conf import settings

from django.db import models
from django.contrib.auth.models import User
from django.utils.deconstruct import deconstructible

@deconstructible
class UploadToUUIDPath:

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]

        filename = '{}.{}'.format(uuid.uuid4(), ext)
        return os.path.join(self.sub_path, filename)


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField()

class Tutorial(models.Model):
    name = models.CharField()
    video = models.FileField(upload_to=UploadToUUIDPath(os.path.join(settings.MEDIA_ROOT), 'tutorial', 'video'))

class Illustrations(models.Model):
    image = models.ImageField(upload_to=UploadToUUIDPath(os.path.join(settings.MEDIA_ROOT, 'tutorial', 'img')))
    tutorial = models.ManyToManyField(Tutorial)
