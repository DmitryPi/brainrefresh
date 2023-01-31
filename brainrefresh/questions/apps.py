from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class QuestionsConfig(AppConfig):
    name = "brainrefresh.questions"
    verbose_name = _("Questions")

    def ready(self):
        try:
            import brainrefresh.questions.signals  # noqa F401
        except ImportError:
            pass
