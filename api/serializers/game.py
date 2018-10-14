from rest_framework import serializers

from api.models import Game, GeneratedQuestion, Question
from api.serializers.quiz import QuizSerializer
from api.serializers.user import UserSerializer


class GeneratedQuestionSerializer(serializers.ModelSerializer):
    question = serializers.SlugRelatedField(read_only=True, slug_field='question')
    number = serializers.IntegerField(read_only=True)
    type = serializers.ChoiceField(choices=Question.TYPE_CHOICES)
    answer = serializers.ListField(
        child=serializers.IntegerField(),
        read_only=True
    )
    timer = serializers.DurationField(read_only=True)
    points = serializers.IntegerField(read_only=True)

    class Meta:
        model = GeneratedQuestion
        fields = ('id', 'question', 'number', 'type', 'answer', 'timer', 'points')


class GameSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer()
    user = UserSerializer(read_only=True)
    current_question = GeneratedQuestionSerializer(read_only=True)
    timer = serializers.DurationField(read_only=True, help_text='Оставшиеся время.')

    class Meta:
        model = Game
        fields = ('id', 'quiz', 'pin', 'title', 'user',
                  'online', 'state', 'current_question', 'timer_on', 'timer',
                  'created_at', 'updated_at', 'finished_at')
        read_only_fields = ('id', 'pin', 'user',
                            'state', 'current_question', 'timer',
                            'created_at', 'updated_at', 'finished_at')
