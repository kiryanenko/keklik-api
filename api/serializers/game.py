from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.fields import empty

from api.models import Game, GeneratedQuestion, Question, Player, Answer, Variant
from api.serializers.quiz import QuizSerializer, VariantSerializer
from api.serializers.user import UserSerializer


class PlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Player
        fields = ('id', 'user', 'rating', 'created_at', 'finished_at')
        read_only_fields = ('rating', 'created_at', 'finished_at')


class AnswerSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = Answer
        fields = ('question', 'answer', 'player', 'correct', 'points')
        extra_kwargs = {
            'question': {'write_only': True},
        }

    def __init__(self, game=None, user=None, data=empty, **kwargs):
        super().__init__(data=data, **kwargs)

        self.game = game
        self.user = user

    def create(self, validated_data):
        return self.game.answer(**validated_data)

    def validate(self, data):
        answer = data['answer']
        question = data['question']

        variants = list(map(lambda var: var.pk, question.variants))
        for variant in answer:
            if variant not in variants:
                raise ValidationError(detail='Unknown variant id "{}". It must be in {}.'.format(variant, variants),
                                      code='unknown_variant')

        try:
            player = self.game.players.get(user=self.user)
            data['player'] = player
        except Player.DoesNotExist:
            raise PermissionDenied()

        return data

    def validate_question(self, value):
        if self.game.current_question != value:
            raise ValidationError(detail='Be late.', code='be_late')

        return value

    # FIXME: invalid docs
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['answer'] = list(map(lambda var_id: VariantSerializer(Variant.objects.get(id=var_id)).data,
                                 instance.answer))
        return ret


class GeneratedQuestionSerializer(serializers.ModelSerializer):
    question = serializers.SlugRelatedField(read_only=True, slug_field='question')
    number = serializers.IntegerField(read_only=True)
    type = serializers.ChoiceField(choices=Question.TYPE_CHOICES)
    variants = VariantSerializer(read_only=True, many=True)
    answer = serializers.ListField(
        child=serializers.IntegerField(),
        read_only=True
    )
    players_answers = AnswerSerializer(read_only=True, many=True)
    timer = serializers.DurationField(read_only=True)
    points = serializers.IntegerField(read_only=True)

    class Meta:
        model = GeneratedQuestion
        fields = ('id', 'question', 'number', 'type', 'variants', 'answer', 'players_answers', 'timer', 'points')


class GameSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer()
    user = UserSerializer(read_only=True)
    players = PlayerSerializer(read_only=True, many=True)
    current_question = GeneratedQuestionSerializer(read_only=True)
    generated_questions = GeneratedQuestionSerializer(read_only=True, many=True)
    timer = serializers.DurationField(read_only=True, help_text='Оставшиеся время.')

    class Meta:
        model = Game
        fields = ('id', 'quiz', 'label', 'user', 'players', 'group',
                  'online', 'state', 'current_question', 'generated_questions', 'timer_on', 'timer',
                  'created_at', 'updated_at', 'state_changed_at', 'finished_at')
        read_only_fields = ('user', 'players', 'state', 'current_question', 'generated_questions', 'timer',
                            'created_at', 'updated_at', 'state_changed_at', 'finished_at')


class CreateGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('quiz', 'label', 'online', 'group')

    def create(self, validated_data):
        return Game.objects.new_game(user=self.context['user'], **validated_data)
