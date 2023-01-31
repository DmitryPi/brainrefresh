from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from brainrefresh.questions.api.views import TagViewSet
from brainrefresh.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("tags", TagViewSet)


app_name = "api"
urlpatterns = router.urls
