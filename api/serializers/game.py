from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from api.models import Game, GeneratedQuestion, Question, Player, Answer
from api.serializers.quiz import QuizSerializer
from api.serializers.user import UserSerializer


class PlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Player
        fields = ('id', 'user', 'created_at', 'finished_at')


class AnswerSerializer(serializers.ModelSerializer):
    player = PlayerSerializer()

    class Meta:
        model = Answer
        fields = ('question', 'answer', 'player')
        extra_kwargs = {
            'question': {'write_only': True},
        }

    def __init__(self, game=None, user=None, **kwargs):
        super().__init__(**kwargs)

        self.game = game
        self.user = user

    def create(self, validated_data):
        return self.game.answer(**validated_data)

    def validate(self, data):
        answer = data['answer']
        question = GeneratedQuestion.objects.get(data['question'])

        variants = question.variants.all()
        for variant in answer:
            if variant not in variants:
                raise ValidationError(detail='Unknown variant id "{}".'.format(variant), code='unknown_variant')

        return data

    def validate_question(self, value):
        question = GeneratedQuestion.objects.get(value)

        if self.game.current_question != question:
            raise ValidationError(detail='Be late.', code='be_late')

        return value

    def validate_player(self, value):
        try:
            player = self.game.players.get(user=self.user)
            return player
        except Player.DoesNotExist:
            raise PermissionDenied()


class GeneratedQuestionSerializer(serializers.ModelSerializer):
    question = serializers.SlugRelatedField(read_only=True, slug_field='question')
    number = serializers.IntegerField(read_only=True)
    type = serializers.ChoiceField(choices=Question.TYPE_CHOICES)
    answer = serializers.ListField(
        child=serializers.IntegerField(),
        read_only=True
    )
    answers = AnswerSerializer(read_only=True, many=True)
    timer = serializers.DurationField(read_only=True)
    points = serializers.IntegerField(read_only=True)

    class Meta:
        model = GeneratedQuestion
        fields = ('id', 'question', 'number', 'type', 'answer', 'answers', 'timer', 'points')


class GameSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer()
    user = UserSerializer(read_only=True)
    players = PlayerSerializer(read_only=True, many=True)
    current_question = GeneratedQuestionSerializer(read_only=True)
    timer = serializers.DurationField(read_only=True, help_text='Оставшиеся время.')

    class Meta:
        model = Game
        fields = ('id', 'quiz', 'label', 'user', 'players',
                  'online', 'state', 'current_question', 'timer_on', 'timer',
                  'created_at', 'updated_at', 'state_changed_at', 'finished_at')
        read_only_fields = ('user', 'players', 'state', 'current_question', 'timer',
                            'created_at', 'updated_at', 'state_changed_at', 'finished_at')


class CreateGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('quiz', 'label', 'online')

    def create(self, validated_data):
        return Game.objects.new_game(user=self.context['user'], **validated_data)
