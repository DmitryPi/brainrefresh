from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Answer, Choice, Question, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fieldsets = ((None, {"fields": (("label", "slug"))}),)
    list_display = ("label", "slug")


def make_published(modeladmin, request, qs):
    qs.update(published=True)


def make_unpublished(modeladmin, request, qs):
    qs.update(published=False)


def update_lang_ru(modeladmin, request, qs):
    qs.update(language=Question.Lang.RU)


def update_lang_en(modeladmin, request, qs):
    qs.update(language=Question.Lang.EN)


make_published.short_description = "Опубликовать"
make_unpublished.short_description = "Снять с публикации"
update_lang_ru.short_description = "Обновить язык на Русский"
update_lang_en.short_description = "Обновить язык на Английский"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    actions = [
        make_published,
        make_unpublished,
        update_lang_ru,
        update_lang_en,
    ]
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


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    readonly_fields = [
        "uuid",
    ]
    filter_horizontal = ["choices"]
