from django.contrib.auth import login, logout
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions, mixins
from rest_framework.compat import authenticate
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.models import User
from api.serializers import CredentialsSerializer, UserSerializer


class SessionView(GenericAPIView):
    serializer_class = CredentialsSerializer

    @swagger_auto_schema(
        operation_summary='Sign In',
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_400_BAD_REQUEST: 'Incorrect username or password.',
        }
    )
    def post(self, request):
        user = authenticate(request, username=request.data.get('username'), password=request.data.get('password'))

        if not user:
            return Response('Incorrect username or password.', status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Sign Out',
    )
    def delete(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = CredentialsSerializer

    @swagger_auto_schema(
        operation_summary='Sign Up',
        request_body=CredentialsSerializer,
        responses={
            status.HTTP_201_CREATED: UserSerializer,
            status.HTTP_400_BAD_REQUEST: 'A user with that username already exists.',
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = CredentialsSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class CurrentUserView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        operation_id='current_profile',
        operation_summary='Профиль текущего юзера',
        request_body=None,
        responses={
            status.HTTP_200_OK: UserSerializer(many=False),
            status.HTTP_401_UNAUTHORIZED: 'UNAUTHORIZED'
        }
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary='Частичное обновление профиля текущего юзера',
        responses={
            status.HTTP_200_OK: UserSerializer(many=False),
            status.HTTP_400_BAD_REQUEST: 'BAD REQUEST',
            status.HTTP_401_UNAUTHORIZED: 'UNAUTHORIZED'
        }
    )
    def patch(self, request):
        """
        Обновить поля профиля текущего юзера
        Обновление частичное (не требуется заполнение всех полей)
        """
        serializer = UserSerializer(request.user, data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
