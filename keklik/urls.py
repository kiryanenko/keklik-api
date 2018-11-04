"""keklik URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from api.urls import media_urlpatterns as api_media_urlpatterns

api_urlpatterns = [
    url(r'^', include('api.urls')),
    url(r'^', include('organization.urls')),
    url(r'^channels/', include('channels_api.urls'))
]

schema_view = get_schema_view(
    openapi.Info(
        title="Keklik API",
        default_version='v1',
        description="Keklik API.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="kiryanenkoav@gmail.com"),
        license=openapi.License(name="BSD License"),

    ),
    patterns=[url(r'^api/', include(api_urlpatterns))],
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)


media_urlpatterns = [
    url(r'^', include(api_media_urlpatterns)),
]

media_schema_view = get_schema_view(
    openapi.Info(
        title="Keklik MEDIA",
        default_version='v1',
        description="Keklik media.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="kiryanenkoav@gmail.com"),
        license=openapi.License(name="BSD License"),

    ),
    patterns=[url(r'^media/', include(media_urlpatterns))],
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(api_urlpatterns)),
    url(r'^media/$', media_schema_view.with_ui('swagger')),
    url(r'^media/', include(media_urlpatterns)),
    url(r'^docs/', schema_view.with_ui('swagger')),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(), name='schema-json'),
    url(r'^swagger/', schema_view.with_ui('swagger'), name='schema-swagger-ui'),
    url(r'^$', schema_view.with_ui('swagger')),
]
