from api.models import User, Persona, EmailConfirmation
from django.dispatch import receiver
from django.db.models.signals import post_save
import hashlib


@receiver(post_save, sender=User)
def create_user_persona(sender, instance, created, **kwargs):
    if created:
        Persona.objects.create(user=instance)

@receiver(post_save, sender=User)
def create_user_email_confirmation(sender, instance, created, **kwargs):
    if created:
        if not instance.is_staff:
            username, email = instance.username, instance.email
            m = hashlib.sha1()
            m.update(bytearray(username + email, 'utf-8'))
            key = m.hexdigest()
            EmailConfirmation.objects.create(user=instance, key=key)
