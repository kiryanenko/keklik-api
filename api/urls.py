from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from api.views.quiz import QuizViewSet
from api.views.user import UserViewSet, SessionView, CurrentUserView, PasswordView

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'quizzes', QuizViewSet)

urlpatterns = [
    url(r'^session/$', SessionView.as_view()),
    url(r'^users/me/$', CurrentUserView.as_view()),
    url(r'^users/me/password/$', PasswordView.as_view()),
    url(r'^', include(router.urls)),
]
