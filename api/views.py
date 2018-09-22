from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.serializers import UserSerializer, ProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class Profile(GenericAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        operation_id='current_profile',
        operation_summary='Профиль текущего юзера',
        request_body=None,
        responses={
            status.HTTP_200_OK: ProfileSerializer(many=False),
            status.HTTP_401_UNAUTHORIZED: 'UNAUTHORIZED'
        }
    )
    def get(self, request):
        """ Профиль текущего юзера """
        serializer = ProfileSerializer(request.user.profile)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary='Частичное обновление профиля текущего юзера',
        responses={
            status.HTTP_200_OK: ProfileSerializer(many=False),
            status.HTTP_400_BAD_REQUEST: 'BAD REQUEST',
            status.HTTP_401_UNAUTHORIZED: 'UNAUTHORIZED'
        }
    )
    def patch(self, request):
        """
        Обновить поля профиля текущего юзера
        Обновление частичное (не требуется заполнение всех полей)
        """
        serializer = ProfileSerializer(request.user.profile, data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
