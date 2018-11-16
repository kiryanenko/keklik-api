from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.models import User, Game, Quiz
from organization.models import Organization, Group
from stats.serializers import StatsSerializer


class StatsView(GenericAPIView):
    serializer_class = StatsSerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: StatsSerializer,
        }
    )
    def get(self, *args, **kwargs):
        serializer = self.get_serializer(data={
            'users_count': User.objects.count(),
            'games_count': Game.objects.count(),
            'organizations_count': Organization.objects.count(),
            'groups_count': Group.objects.count(),
            'quizzes_count': Quiz.objects.count(),
        })
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
