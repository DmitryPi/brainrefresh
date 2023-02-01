from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from brainrefresh.questions.api.views import QuestionViewSet, TagViewSet
from brainrefresh.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("tags", TagViewSet, basename="tag")
router.register("questions", QuestionViewSet, basename="question")


app_name = "api"
urlpatterns = router.urls
