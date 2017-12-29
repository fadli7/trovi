import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.template.defaultfilters import filesizeformat

from api.deconstructible.validators import FileValidator
from api.deconstructible.utils import UploadToUUIDPath
# Create your models here.

HTML_VIDEOS = ('video/mp4', 'video/webm', 'video/ogg')

class User(AbstractUser):
    email = models.EmailField(unique=True)

class Persona(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(null=True, upload_to=UploadToUUIDPath(os.path.join(settings.MEDIA_ROOT, 'user', 'persona')))
    description = models.TextField(null=True)

    def __str__(self):
        return self.user.username

class EmailConfirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=64)
    time = models.DateTimeField(auto_now_add=True)

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
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to=UploadToUUIDPath(os.path.join('media/tutorial/illustration/')))
    description = models.TextField()

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
