from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from api.views.games import GameViewSet
from api.views.quizzes import QuizViewSet, UserQuizzesView, CurrentUserQuizzesView
from api.views.users import UserViewSet, SessionView, CurrentUserView, PasswordView

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'games', GameViewSet)

urlpatterns = [
    url(r'^session/$', SessionView.as_view()),
    url(r'^users/me/$', CurrentUserView.as_view()),
    url(r'^users/me/password/$', PasswordView.as_view()),
    url(r'^users/me/quizzes/$', CurrentUserQuizzesView.as_view()),
    url(r'^users/(?P<username>\w+)/quizzes/$', UserQuizzesView.as_view()),
    url(r'^', include(router.urls)),
]
