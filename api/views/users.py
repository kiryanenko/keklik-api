from django.contrib.auth import login, logout
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions, mixins
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.models import User
from api.serializers.credentials import CredentialsSerializer, ChangePasswordSerializer
from api.serializers.user import UserSerializer
from api.serializers.user_detail import UserDetailSerializer
from api.utils.views import status_text


class SessionView(ObtainAuthToken):
    @swagger_auto_schema(
        operation_summary='Sign In',
        request_body=AuthTokenSerializer,
        responses={
            status.HTTP_200_OK: CredentialsSerializer,
            status.HTTP_400_BAD_REQUEST: 'Incorrect username or password.',
        }
    )
    def post(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(CredentialsSerializer(user, context={'request': request}).data)

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
        request_body=AuthTokenSerializer,
        responses={
            status.HTTP_201_CREATED: CredentialsSerializer,
            status.HTTP_400_BAD_REQUEST: 'A user with that username already exists.',
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = CredentialsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        login(request, user)
        return Response(CredentialsSerializer(user, context={'request': request}).data, status=status.HTTP_201_CREATED)


class CurrentUserView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        operation_id='current_profile',
        operation_summary='Профиль текущего юзера',
        responses={
            status.HTTP_200_OK: UserDetailSerializer,
            status.HTTP_403_FORBIDDEN: status_text(status.HTTP_403_FORBIDDEN)
        }
    )
    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary='Частичное обновление профиля текущего юзера',
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_400_BAD_REQUEST: status_text(status.HTTP_400_BAD_REQUEST),
            status.HTTP_403_FORBIDDEN: status_text(status.HTTP_403_FORBIDDEN)
        }
    )
    def patch(self, request):
        """
        Обновить поля профиля текущего юзера
        Обновление частичное (не требуется заполнение всех полей)
        """
        serializer = UserSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        operation_id='change_password',
        responses={
            status.HTTP_200_OK: status_text(status.HTTP_200_OK),
            status.HTTP_400_BAD_REQUEST: status_text(status.HTTP_400_BAD_REQUEST),
            status.HTTP_403_FORBIDDEN: status_text(status.HTTP_403_FORBIDDEN)
        }
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(status=status.HTTP_200_OK)
