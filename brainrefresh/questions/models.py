import uuid as uuid_lib

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import FieldTracker

from brainrefresh.utils.misc import get_unique_slug

from .managers import QuestionManager

User = get_user_model()


class Tag(models.Model):
    label = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110, blank=True, db_index=True, unique=True)
    tracker = FieldTracker(fields=["label"])

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if not self.slug or self.label != self.tracker.previous("label"):
            self.slug = get_unique_slug(Tag, self.label)
        return super().save(*args, **kwargs)


class Question(models.Model):
    class Lang(models.TextChoices):
        EN = "EN"
        RU = "RU"

    # managers
    objects = QuestionManager()
    # related fields
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="%(class)ss")
    tags = models.ManyToManyField(
        Tag, blank=True, related_name="%(class)ss", related_query_name="%(class)s"
    )
    # fields
    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False)
    title = models.CharField(max_length=100)
    text = models.TextField(blank=True)
    explanation = models.TextField(blank=True)
    language = models.CharField(max_length=5, choices=Lang.choices, default=Lang.EN)
    published = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")

    def __str__(self):
        return self.title


class Choice(models.Model):
    # related fields
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="%(class)ss"
    )
    # fields
    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Choice")
        verbose_name_plural = _("Choice")

    def __str__(self):
        return f"{self.question.title} : {str(self.uuid)}"


class Answer(models.Model):
    """
    TODO: choices question validation (prevent adding choices from another question)
    """

    # related fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="%(class)ss")
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="%(class)ss"
    )
    choices = models.ManyToManyField(Choice, related_name="%(class)ss")
    # fields
    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")

    def __str__(self):
        return f"{self.user.username} answered {self.question.title}"
