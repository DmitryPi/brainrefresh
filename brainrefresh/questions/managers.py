from django.db import models


class QuestionQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class QuestionManager(models.Manager):
    def get_queryset(self):
        return QuestionQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()
