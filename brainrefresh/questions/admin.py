from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Choice, Question, Tag


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    readonly_fields = [
        "uuid",
        "updated_at",
        "created_at",
    ]
    fieldsets = (
        (None, {"fields": ("uuid", "user", "language")}),
        (
            _("Вопрос"),
            {"fields": ("title", "text", "explanation")},
        ),
        ("Теги", {"fields": ["tags"]}),
        (
            None,
            {"fields": ("published",)},
        ),
    )
    list_display = [
        "title",
        "uuid",
        "language",
        "published",
        "updated_at",
        "created_at",
    ]
    filter_horizontal = ["tags"]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    readonly_fields = [
        "uuid",
    ]
    fieldsets = (
        (None, {"fields": ("uuid", "question")}),
        (
            _("Вариант ответа"),
            {
                "fields": (
                    "text",
                    "is_correct",
                )
            },
        ),
    )
    list_display = ("__str__", "is_correct")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fieldsets = ((None, {"fields": (("label", "slug"))}),)
    list_display = ("label", "slug")
