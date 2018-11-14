import io
import random

import xlsxwriter
from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from api.models import Quiz, User, Question, Variant
from api.utils.xlsx import XslStyles
from organization.models import Group


class GameManager(models.Manager):
    @transaction.atomic
    def new_game(self, quiz, user, label='', online=False, group=None):
        game = self.create(quiz=quiz, label=label, online=online, user=user, group=group)

        for question in quiz.questions.all():
            GeneratedQuestion.objects.generate(game, question)

        if group is not None:
            group.organization.quizzes.add(quiz)

        return game


def report_path(instance, filename):
    return 'reports/%Y/%m/%d/Game_{}_%Y-%m-%d_%H-%M.xlsx'.format(instance.pk)


class Game(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    label = models.CharField(max_length=300, blank=True)
    online = models.BooleanField(default=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, related_name='games')
    base_game = models.ForeignKey('Game', on_delete=models.CASCADE, null=True)

    PLAYERS_WAITING_STATE = 'players_waiting'
    ANSWERING_STATE = 'answering'
    CHECK_STATE = 'check'
    FINISH_STATE = 'finish'
    STATE_CHOICES = (
        (PLAYERS_WAITING_STATE, 'Ожидание игроков'),
        (ANSWERING_STATE, 'Игроки отвечают на вопросы'),
        (CHECK_STATE, 'Показ правильного ответа'),
        (FINISH_STATE, 'Финиш'),
    )
    state = models.CharField(max_length=15, choices=STATE_CHOICES, db_index=True, default=PLAYERS_WAITING_STATE)

    current_question = models.ForeignKey('GeneratedQuestion', on_delete=models.CASCADE, null=True, related_name='+')
    timer_on = models.BooleanField(default=True, db_index=True)

    # TODO: Saving report
    # report = models.FileField(null=True, upload_to=report_path)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True,
                                      help_text='Дата обновляется при любых обновлениях снапшота игры: '
                                                'изменении модели, присоединение игрока, при новом ответе и т.д.')
    state_changed_at = models.DateTimeField(auto_now_add=True,
                                            help_text='Дата обновляется при изменении состояния `state` '
                                                      'и при изменении вопроса `current_question`.')
    finished_at = models.DateTimeField(null=True, db_index=True)

    objects = GameManager()

    joined_player = Signal(providing_args=['player'])
    question_changed = Signal()
    answered = Signal(providing_args=['answer'])
    check_signal = Signal(providing_args=['question'])
    finished = Signal()

    CAN_JOIN_TO_GOING_GAME = True

    @property
    def timer(self):
        if self.current_question is None:
            return None

        timer = self.current_question.question.timer
        if timer is None:
            return None

        return timezone.now() - self.state_changed_at - timer

    def finish(self):
        now = timezone.now()

        self.current_question = None
        self.state = self.FINISH_STATE
        self.state_changed_at = now

        for player in self.players.all():
            player.finish()

        self.save()

        self.finished.send(self)

    def join(self, user):
        if not self.CAN_JOIN_TO_GOING_GAME and self.state != self.PLAYERS_WAITING_STATE:
            raise ValidationError(detail='Game state is not "players_waiting".', code='not_players_waiting')

        player, created = Player.objects.get_or_create(game=self, user=user)
        if created:
            self.save()
            self.joined_player.send(self, player=player)
        return player

    def next_question(self):
        if self.state == self.FINISH_STATE:
            return self.current_question    # None

        now = timezone.now()

        try:
            if self.current_question is None:
                self.current_question = self.generated_questions.first_question
            else:
                self.current_question = self.current_question.next
            self.state = self.ANSWERING_STATE
            self.state_changed_at = now
            self.current_question.started_at = now
            self.save()
            self.current_question.save()
            self.question_changed.send(self)

        except GeneratedQuestion.DoesNotExist:
            self.finish()

        return self.current_question

    def answer(self, player, answer, question=None):
        if question is None:
            question = self.current_question

        correct = question.answer == answer
        points = self.count_points(question, correct)

        player_answer, created = Answer.objects.update_or_create(
            question=question,
            player=player,
            defaults={'answer': answer, 'correct': correct, 'points': points}
        )

        self.save()

        self.answered.send(self, answer=player_answer)
        return player_answer

    def check_state(self):
        if self.state != self.ANSWERING_STATE:
            raise ValidationError('Now not answering state', code='not_answering')

        self.state = self.CHECK_STATE
        self.save()

        self.check_signal.send(self, question=self.current_question)

        return self.current_question

    def make_report(self):
        output = io.BytesIO()
        report = xlsxwriter.Workbook(output)
        styles = XslStyles(report)

        self.report_main_page(report, styles)
        self.report_answers_page(report, styles)

        report.close()
        output.seek(0)
        return output

    def report_main_page(self, report, styles):
        worksheet = report.add_worksheet('Общее')

        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 50)

        worksheet.write('A1', 'Отчет по проведенной викторине № {} за {}'.format(
            self.pk, self.updated_at.now().strftime('%Y-%m-%d %H:%M')), styles.title)
        worksheet.set_row(0, 30)
        worksheet.write('A2', self.label)

        worksheet.write('A3', 'Дата:', styles.bold)
        worksheet.write('B3', self.updated_at.now().strftime('%Y-%m-%d %H:%M'))

        worksheet.write('A4', 'Организация:', styles.bold)
        worksheet.write('B4', self.group.organization.name if self.group is not None else '-')

        worksheet.write('A5', 'Группа:', styles.bold)
        worksheet.write('B5', self.group.name if self.group is not None else '-')

        worksheet.write('A7', 'Количество участников:', styles.bold)
        players_count = self.players.all().count()
        worksheet.write_number('B7', players_count)

        worksheet.write('A8', 'Процент правильных ответов:', styles.bold)
        success_answers_count = Answer.objects.filter(question__game=self, correct=True).count()
        questions_count = self.generated_questions.all().count()
        answers_count = players_count * questions_count
        if answers_count == 0:
            answers_count = 1
        worksheet.write_number('B8', success_answers_count / answers_count * 100)

    def report_answers_page(self, report, styles):
        worksheet = report.add_worksheet('Ответы участников')

        players = self.players.all().order_by('user__last_name', 'user__first_name', 'user__patronymic',
                                              'user__username')
        players_count = players.count()
        questions = self.generated_questions.order_by('question__number')

        player_header_row = 5
        question_total_row = player_header_row + players_count + 1

        self.report_questions(worksheet, styles, questions, 3, question_total_row)
        self.report_players_answers(worksheet, styles, players, questions, player_header_row)

    def report_questions(self, worksheet, styles, questions, data_start_col, total_row):
        question_num_row = 0
        worksheet.write(question_num_row, 0, '№ вопроса:', styles.bold)
        question_text_row = 1
        worksheet.write(question_text_row, 0, 'Вопрос:', styles.bold)
        variants_row = 2
        worksheet.write(variants_row, 0, 'Варианты:', styles.bold)
        answer_row = 3
        worksheet.write(answer_row, 0, 'Ответ:', styles.bold)
        points_row = 4
        worksheet.write(points_row, 0, 'Макс. балл за правильный ответ:', styles.bold)

        questions_count = questions.count()
        players_count = self.players.all().count()

        success_answers_count_row = total_row
        worksheet.write(success_answers_count_row, 0, 'Количество правильных ответов:', styles.bold)
        answers_count_row = success_answers_count_row + 1
        worksheet.write(answers_count_row, 0, 'Количество ответов:', styles.bold)
        success_answers_percent_row = answers_count_row + 1
        worksheet.write(success_answers_percent_row, 0, 'Процент правильных ответов:', styles.bold)

        # Заполняю вопросы
        for col, question in enumerate(questions, data_start_col):
            worksheet.write_number(question_num_row, col, question.number, styles.bold)
            worksheet.write(question_text_row, col, question.question.question)
            worksheet.write(variants_row, col, question.variants_str)
            worksheet.write(answer_row, col, question.question.answer_str)
            worksheet.write_number(points_row, col, question.question.points)

            success_answers_count = Answer.objects.filter(question=question, correct=True).count()
            worksheet.write_number(success_answers_count_row, col, success_answers_count)
            answers_count = Answer.objects.filter(question=question).count()
            worksheet.write_number(answers_count_row, col, answers_count)
            success_answers_percent = success_answers_count / players_count * 100 if players_count > 0 else 0
            worksheet.write_number(success_answers_percent_row, col, success_answers_percent)

        worksheet.set_column(data_start_col, data_start_col + questions_count - 1, 20)

    def report_players_answers(self, worksheet, styles, players, questions, player_header_row):
        questions_count = questions.count()

        index_col = 0
        worksheet.write(player_header_row, index_col, '№', styles.bold)
        login_col = 1
        worksheet.write(player_header_row, login_col, 'Логин', styles.bold)
        name_col = 2
        worksheet.write(player_header_row, name_col, 'ФИО', styles.bold)
        worksheet.set_column(name_col, name_col, 30)
        data_start_col = name_col + 1

        success_answers_count_col = data_start_col + questions_count
        worksheet.write(player_header_row, success_answers_count_col, 'Кол-во правильных ответов', styles.bold)
        worksheet.set_column(success_answers_count_col, success_answers_count_col, 15)

        success_answers_percent_col = success_answers_count_col + 1
        worksheet.write(player_header_row, success_answers_percent_col, 'Процент правильных ответов', styles.bold)
        worksheet.set_column(success_answers_percent_col, success_answers_percent_col, 15)

        rating_col = success_answers_percent_col + 1
        worksheet.write(player_header_row, rating_col, 'Рейтинг', styles.bold)

        # Заполняю ответы
        row = player_header_row + 1
        for i, player in enumerate(players, 1):
            worksheet.write_number(row, index_col, i)
            worksheet.write(row, login_col, player.user.username)
            worksheet.write(row, name_col, player.user.full_name)

            for col, question in enumerate(questions, data_start_col):
                try:
                    answer = Answer.objects.get(player=player, question=question)
                    style = styles.bg_green if answer.correct else styles.bg_red
                    worksheet.write(row, col, answer.answer_str, style)
                except Answer.DoesNotExist:
                    worksheet.write(row, col, '-', styles.bg_gray)

            success_answers_count = Answer.objects.filter(player=player, correct=True).count()
            worksheet.write_number(row, success_answers_count_col, success_answers_count)
            success_answers_percent = success_answers_count / questions_count * 100
            worksheet.write_number(row, success_answers_percent_col, success_answers_percent)
            worksheet.write_number(row, rating_col, player.rating)

            row += 1

    @property
    def report_filename(self):
        return 'Game_{}__{}.xlsx'.format(self.pk, self.updated_at.strftime('%Y-%m-%d_%H-%M'))

    @property
    def players_rating(self):
        return self.players.order_by('-rating', 'id')

    @staticmethod
    def count_points(generated_question, correct=True):
        if not correct:
            return 0

        timer = generated_question.question.timer
        coefficient = (timezone.now() - generated_question.started_at) / timer if timer is not None else 1
        if coefficient < 0:
            coefficient = 0
        return generated_question.question.points + generated_question.question.points * coefficient

    def __str__(self):
        return '[{}] {} {} {}'.format(self.pk, self.state, self.label, self.quiz)


class GeneratedQuestionManager(models.Manager):
    def generate(self, game, question):
        variants_order = list(map(lambda variant: variant.pk, question.variants.all()))
        random.shuffle(variants_order)
        return self.create(game=game, question=question, variants_order=variants_order)

    @property
    def first_question(self):
        return self.get(question__number=1)


class GeneratedQuestion(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='generated_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    variants_order = ArrayField(
        models.IntegerField(), help_text='ID вариантов. При создании новой игры варианты перемешиваются.'
    )
    started_at = models.DateTimeField(null=True)

    objects = GeneratedQuestionManager()

    @property
    def number(self):
        return self.question.number

    @property
    def type(self):
        return self.question.type

    @property
    def answer(self):
        return self.question.answer

    @property
    def timer(self):
        return self.question.timer

    @property
    def points(self):
        return self.question.points

    @property
    def next(self):
        return GeneratedQuestion.objects.get(game=self.game, question__number=self.number + 1)

    @property
    def variants(self):
        return list(map(lambda variant_id: self.question.variants.get(id=variant_id), self.variants_order))

    @property
    def variants_str(self):
        variants = list(map(lambda variant: variant.variant, self.variants))
        return '; '.join(variants)

    def __str__(self):
        return '[{}] {}'.format(self.pk, self.question)


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players')
    rating = models.IntegerField(default=0, help_text='Рейтинг за игру.')
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, db_index=True)

    class Meta:
        unique_together = ('user', 'game')

    def finish(self):
        self.finished_at = timezone.now()
        self.save()

    def __str__(self):
        return '[{}] {}'.format(self.pk, self.user)


class Answer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    question = models.ForeignKey(GeneratedQuestion, on_delete=models.CASCADE, related_name='players_answers')
    answer = ArrayField(
        models.IntegerField(), help_text='ID правильных вариантов ответов.\n'
                                         'Для Single вопросов массив состоит из одного элемента.\n'
                                         'Для Sequence важен порядок.'
    )
    correct = models.BooleanField(default=False)
    points = models.IntegerField(default=0, help_text='Начисленные очки за ответ.')
    answered_at = models.DateTimeField(auto_now=True)

    @property
    def answer_str(self):
        answer = list(map(lambda ans: Variant.objects.get(pk=ans).variant, self.answer))
        return '; '.join(answer)

    def __str__(self):
        return '{}. {} - {}'.format(self.question.number, self.player, self.answer)


@receiver(post_save, sender=Answer)
def update_rating(instance, **kwargs):
    player = instance.player
    user = player.user

    rating_before = player.rating
    player.rating = Answer.objects.filter(player=player).aggregate(Sum('points'))['points__sum']
    user.rating += player.rating - rating_before

    player.save()
    user.save()
