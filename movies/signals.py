from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import Movies



@receiver(pre_save, sender=Movies)
def set_movie_slug(sender, instance, **kwargs):
    base_slug = slugify(instance.title)

    if not instance.slug:
        instance.slug = generate_unique_slug(base_slug, instance.pk)

    else:
        try:
            old = Movies.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            old = None
        
        if old and old.title != instance.title:
            instance.slug = generate_unique_slug(base_slug, instance.pk)


def generate_unique_slug(base_slug, instance_pk=None):
    unique_slug = base_slug
    counter = 1
    while Movies.objects.filter(slug=unique_slug).exclude(pk=instance_pk).exists():
        unique_slug = f"{base_slug}-{counter}"
        counter += 1

    return unique_slug
