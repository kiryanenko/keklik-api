from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from api import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^profile/', views.Profile.as_view()),
]
