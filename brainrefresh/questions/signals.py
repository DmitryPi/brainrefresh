from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Choice, Question, Tag


@receiver([post_save, post_delete], sender=Tag)
def invalidate_cache_for_tag(*args, **kwargs):
    """TODO: redis cache with tag-based invalidation"""
    cache.clear()


@receiver([post_save, post_delete], sender=Question)
def invalidate_cache_for_question(*args, **kwargs):
    """TODO: redis cache with tag-based invalidation"""
    cache.clear()


@receiver([post_save, post_delete], sender=Choice)
def invalidate_cache_for_choice(*args, **kwargs):
    """TODO: redis cache with tag-based invalidation"""
    cache.clear()
