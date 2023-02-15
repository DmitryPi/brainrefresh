from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Answer, Choice, Question, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fieldsets = ((None, {"fields": (("label", "slug"))}),)
    list_display = ("label", "slug", "question_count")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("questions")


def make_published(modeladmin, request, qs):
    qs.update(is_published=True)


def make_unpublished(modeladmin, request, qs):
    qs.update(is_published=False)


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
        "is_multichoice",
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
            {"fields": ("is_multichoice", "is_published")},
        ),
    )
    list_display = [
        "title",
        "uuid",
        "language",
        "is_multichoice",
        "is_published",
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("question")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    readonly_fields = [
        "uuid",
    ]
    fieldsets = (
        (None, {"fields": ("uuid", "user")}),
        (None, {"fields": ("choices",)}),
        (None, {"fields": ("is_correct",)}),
    )
    list_display = ("__str__", "is_correct", "created_at")
    list_select_related = ["question", "user"]
    raw_id_fields = ["choices"]

    def get_queryset(self, request, *args, **kwargs):
        queryset = super().get_queryset(request, *args, **kwargs)
        return queryset.select_related("question", "user")
