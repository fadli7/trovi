import os
import uuid
import magic
from django.conf import settings

from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.deconstruct import deconstructible
from django.template.defaultfilters import filesizeformat

@deconstructible
class UploadToUUIDPath:

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]

        filename = '{}.{}'.format(uuid.uuid4(), ext)
        return os.path.join(self.sub_path, filename)

@deconstructible
class FileValidator:
    error_messages = {
     'max_size': ("Ensure this file size is not greater than %(max_size)s."
                  " Your file size is %(size)s."),
     'min_size': ("Ensure this file size is not less than %(min_size)s. "
                  "Your file size is %(size)s."),
     'content_type': "Files of type %(content_type)s are not supported.",
    }

    def __init__(self, max_size=None, min_size=None, content_types=()):
        self.max_size = max_size
        self.min_size = min_size
        self.content_types = content_types

    def __call__(self, data):
        if self.max_size is not None and data.size > self.max_size:
            params = {
                'max_size': filesizeformat(self.max_size), 
                'size': filesizeformat(data.size),
            }
            raise ValidationError(self.error_messages['max_size'],
                                   'max_size', params)

        if self.min_size is not None and data.size < self.min_size:
            params = {
                'min_size': filesizeformat(self.mix_size),
                'size': filesizeformat(data.size)
            }
            raise ValidationError(self.error_messages['min_size'],
                                   'min_size', params)

        if self.content_types:
            content_type = magic.from_buffer(data.read(), mime=True)
            if content_type not in self.content_types:
                params = { 'content_type': content_type }
            raise ValidationError(self.error_messages['content_type'],
                                   'content_type', params)

    def __eq__(self, other):
        return isinstance(other, FileValidator)

# Create your models here.

class Persona(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(null=True, upload_to=UploadToUUIDPath(os.path.join(settings.MEDIA_ROOT, 'user', 'persona')))
    description = models.TextField(null=True)

@receiver(post_save, sender=User)
def create_user_persona(sender, instance, created, **kwargs):
    if created:
        Persona.objects.create(user=instance)

class Tag(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Tutorial(models.Model):
    tags = models.ManyToManyField(Tag)
    buyers = models.ManyToManyField(User)
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    video = models.FileField(upload_to=UploadToUUIDPath(os.path.join(settings.MEDIA_ROOT, 'tutorial', 'video')),
            validators=[FileValidator(content_types='video')])
    description = models.TextField()

    def __str__(self):
        return self.name

class Illustration(models.Model):
    tutorial = models.ManyToManyField(Tutorial)
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to=UploadToUUIDPath(os.path.join(settings.MEDIA_ROOT, 'tutorial', 'img')))

    def __str__(self):
        return str(self.id) + " " + self.tutorial.name

class Transaction(models.Model):
    user = models.ForeignKey(User)
    tutorial = models.ForeignKey(Tutorial)
    payment_proof = models.ImageField(upload_to=UploadToUUIDPath(os.path.join(settings.MEDIA_ROOT, 'user', 'payment_proof')))
    is_reviewed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)
