from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import UserSerializer, ProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class Profile(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = ProfileSerializer(request.user.profile)
        return Response(serializer.data)
