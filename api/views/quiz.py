from rest_framework import permissions, filters
from rest_framework.viewsets import ModelViewSet

from api.models import Quiz
from api.serializers import QuizSerializer


class QuizViewSet(ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('id', 'version_date', 'title', 'rating')
    ordering = ('-version_date', '-id')     # FIXME: Потом сортировать по рейтингу

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
