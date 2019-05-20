from channels import Group
from channels_api import mixins, detail_action, permissions
from channels_api.bindings import ReadOnlyResourceBinding
from django.dispatch import receiver
from rest_framework.exceptions import PermissionDenied

from api.models import Game, Player, Answer, GeneratedQuestion
from api.serializers.game import GameSerializer, PlayerSerializer, AnswerSerializer, GeneratedQuestionSerializer


class GroupMixin(object):
    @classmethod
    def broadcast(cls, action, pk=None, data=None, model=None):
        if model is None:
            model = cls.model

        Group(cls.group_name(action, pk)).send(cls.encode(cls.stream, {
            'action': action,
            'pk': pk,
            'data': data,
            'model': model.__name__
        }))

    @classmethod
    def group_name(cls, action, id=None):
        return cls()._group_name(action, id=id)


class GameBinding(GroupMixin, mixins.SubscribeModelMixin, ReadOnlyResourceBinding):
    model = Game
    stream = "games"
    serializer_class = GameSerializer
    queryset = Game.objects\
        .select_related('quiz__user', 'user', 'group__organization', 'current_question')\
        .prefetch_related('players__user',
                          'quiz__tags',
                          'quiz__questions',
                          'generated_questions',
                          'generated_questions__question',
                          'generated_questions__players_answers',)
    permission_classes = (permissions.IsAuthenticated,)

    JOIN_SUB = 'join'
    NEXT_QUESTION_SUB = 'next_question'
    ANSWER_SUB = 'answer'
    CHECK_SUB = 'check'
    FINISH_SUB = 'finish'

    @detail_action()
    def join(self, pk, data=None, **kwargs):
        game = self.get_object_or_404(pk)
        game.join(self.user)
        return GameSerializer(game).data, 200

    @detail_action()
    def next_question(self, pk, data=None, **kwargs):
        game = self.get_object_or_404(pk)

        if game.user != self.user:
            raise PermissionDenied()

        game.next_question()
        return GameSerializer(game).data, 200

    @detail_action()
    def answer(self, pk, data=None, **kwargs):
        game = self.get_object_or_404(pk)
        serializer = AnswerSerializer(game=game, user=self.user, data=data)
        serializer.is_valid(raise_exception=True)
        answer = serializer.save()
        return serializer.data, 200

    @detail_action()
    def check(self, pk, data=None, **kwargs):
        game = self.get_object_or_404(pk)

        if game.user != self.user:
            raise PermissionDenied()

        question = game.check_state()

        return GeneratedQuestionSerializer(question).data, 200

    @staticmethod
    @receiver(Game.joined_player)
    def join_sub(sender, player, **kwargs):
        GameBinding.broadcast(GameBinding.JOIN_SUB, pk=sender.pk, data=PlayerSerializer(player).data, model=Player)

    @staticmethod
    @receiver(Game.question_changed)
    def next_question_sub(sender, **kwargs):
        GameBinding.broadcast(GameBinding.NEXT_QUESTION_SUB, pk=sender.pk, data=GameSerializer(sender).data)

    @staticmethod
    @receiver(Game.answered)
    def answer_sub(sender, answer,**kwargs):
        GameBinding.broadcast(GameBinding.ANSWER_SUB, pk=sender.pk, data=AnswerSerializer(instance=answer).data,
                              model=Answer)

    @staticmethod
    @receiver(Game.check_signal)
    def check_sub(sender, question, **kwargs):
        GameBinding.broadcast(GameBinding.CHECK_SUB, pk=sender.pk, data=GeneratedQuestionSerializer(question).data,
                              model=GeneratedQuestion)

    @staticmethod
    @receiver(Game.finished)
    def finish_sub(sender, **kwargs):
        GameBinding.broadcast(GameBinding.FINISH_SUB, pk=sender.pk, data=GameSerializer(sender).data)
