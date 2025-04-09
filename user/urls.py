from django.urls import path
from rest_framework.routers import DefaultRouter
from user.views import UserViewSet, CurrentUserView

app_name = "user"

router = DefaultRouter()
router.register(r"user", UserViewSet, basename="user")

urlpatterns = router.urls

urlpatterns += [
    path("current_user/", CurrentUserView.as_view(), name="current_user"),
]
