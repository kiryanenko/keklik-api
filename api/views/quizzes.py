from rest_framework import permissions, filters
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.viewsets import ModelViewSet

from api.models import Quiz, User
from api.serializers.quiz import QuizSerializer


class QuizViewSet(ModelViewSet):
    queryset = Quiz.objects.filter(old_version__isnull=True)
    serializer_class = QuizSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('id', 'version_date', 'title', 'rating')
    ordering = ('-rating', '-version_date', '-id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserQuizzesView(ListAPIView):
    serializer_class = QuizSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('id', 'version_date', 'title', 'rating')
    ordering = ('-rating', '-version_date', '-id')

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        return Quiz.objects.filter(user=user, old_version__isnull=True)


class CurrentUserQuizzesView(UserQuizzesView):
    permission_classes = (permissions.IsAuthenticated,)
    ordering = ('-version_date', '-id')

    def get_queryset(self):
        user = self.request.user
        return Quiz.objects.filter(user__username=user, old_version__isnull=True)
