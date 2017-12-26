import os
import uuid
import magic
from django.conf import settings
import hashlib

from django.core.exceptions import ValidationError
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.utils.deconstruct import deconstructible
from django.template.defaultfilters import filesizeformat

HTML_VIDEOS = ('video/mp4', 'video/webm', 'video/ogg')

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
            print(content_type, self.content_types)
            if content_type not in self.content_types:
                params = { 'content_type': content_type }
                raise ValidationError(self.error_messages['content_type'],
                                       'content_type', params)

    def __eq__(self, other):
        return isinstance(other, FileValidator)

# Create your models here.

class User(AbstractUser):

    email = models.EmailField(unique=True)

class Persona(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(null=True, upload_to=UploadToUUIDPath(os.path.join(settings.MEDIA_ROOT, 'user', 'persona')))
    description = models.TextField(null=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_persona(sender, instance, created, **kwargs):
    if created:
        Persona.objects.create(user=instance)

class EmailConfirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=64)
    time = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=User)
def create_user_email_confirmation(sender, instance, created, **kwargs):
    if created:
        username, email = instance.username, instance.email
        m = hashlib.sha256()
        m.update(bytearray(username + email + str(uuid.uuid4()), 'utf-8'))
        key = m.hexdigest()
        EmailConfirmation.objects.create(user=instance, key=key)

class Tag(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Tutorial(models.Model):
    banner = models.ImageField(upload_to=UploadToUUIDPath('media/tutorial/banner/'))
    tags = models.ManyToManyField(Tag, blank=True)
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    video = models.FileField(upload_to=UploadToUUIDPath(os.path.join('media/tutorial/video/')),
            validators=[FileValidator(content_types=HTML_VIDEOS)])
    description = models.TextField()

    def __str__(self):
        return self.name

class Illustration(models.Model):
    tutorial = models.ManyToManyField(Tutorial)
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to=UploadToUUIDPath(os.path.join('media/tutorial/illustration/')))

    def __str__(self):
        return str(self.id) + " " + self.tutorial.name

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE)
    price = models.IntegerField()
    payment_proof = models.ImageField(upload_to=UploadToUUIDPath(os.path.join('media/user/payment_proof/')))
    is_reviewed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

