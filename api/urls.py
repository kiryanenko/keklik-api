from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from api import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    url(r'^session/$', views.SessionView.as_view()),
    url(r'^users/me/$', views.CurrentUserView.as_view()),
    url(r'^users/me/password/$', views.PasswordView.as_view()),
    url(r'^', include(router.urls)),
]
