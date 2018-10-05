from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from api.models import Quiz
from api.serializers import QuizSerializer


class QuizViewSet(ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
