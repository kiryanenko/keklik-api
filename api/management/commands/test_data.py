import random
import string
import traceback

from django.core.management import BaseCommand

from api.models import User, Quiz, Game
from organization.models import Organization, Group, GroupMember


def random_word(length):
    letters = string.ascii_lowercase
    return ''.join(random.sample(letters, length))


class Command(BaseCommand):
    help = 'Заполняет БД тестовыми данными'

    def add_arguments(self, parser):
        parser.add_argument('--users_cnt', dest='users_cnt', type=int, default=1000)
        parser.add_argument('--organizations_cnt', dest='organizations_cnt', type=int, default=100)
        parser.add_argument('--groups_cnt', dest='groups_cnt', type=int, default=500)
        parser.add_argument('--members_cnt', dest='members_cnt', type=int, default=1000)
        parser.add_argument('--games_cnt', dest='games_cnt', type=int, default=10000)
        parser.add_argument('--players_cnt', dest='players_cnt', type=int, default=10000)

    def handle(self, users_cnt, organizations_cnt, groups_cnt, members_cnt, games_cnt, players_cnt, *args, **options):
        admin = User.objects.filter(is_superuser=True).first()

        print('Создаю {} новых пользователей...'.format(users_cnt))
        for i in range(users_cnt):
            username = str(i) + random_word(10)
            email = '{}@test.ru'.format(username)
            pwd = '123456'
            try:
                user = User.objects.create_user(username, email, pwd)
                print('{}/{} Добавлен новый пользователь {}'.format(i + 1, users_cnt, user))
            except Exception:
                traceback.print_exc()
                print('Ошибка при добавлении {}'.format(username))

        print('\nСоздаю {} новых организаций...'.format(users_cnt))
        for i in range(organizations_cnt):
            name = str(i) + random_word(10)
            try:
                org = Organization.objects.create_organization(name, admin)
                print('{}/{} Добавлена новая организация'.format(i + 1, organizations_cnt, org))
            except Exception:
                traceback.print_exc()
                print('Ошибка при добавлении {}'.format(name))

        print('\nСоздаю {} новых групп организаций...'.format(groups_cnt))
        for i in range(groups_cnt):
            name = str(i) + random_word(10)
            organization = Organization.objects.order_by('?').first()
            try:
                group = Group.objects.create(name=name, organization=organization)
                print('{}/{} Добавлена новая группа {} организации {}'.format(i + 1, groups_cnt, group, organization))
            except Exception:
                traceback.print_exc()
                print('Ошибка при добавлении {}'.format(name))

        print('\nСоздаю {} новых членов групп организаций...'.format(members_cnt))
        for i in range(members_cnt):
            role = random.choice([GroupMember.STUDENT_ROLE, GroupMember.TEACHER_ROLE])
            group = Group.objects.order_by('?').first()
            user = User.objects.filter(email__contains='@test.ru').exclude(member_of_groups__group=group).order_by('?').first()
            try:
                group = GroupMember.objects.create(user=user, group=group, role=role)
                print('{}/{} Добавлен новый член {} групп {} организаций'.format(i + 1, members_cnt, user, group))
            except Exception:
                traceback.print_exc()
                print('Ошибка при добавлении {} в группу {}'.format(user, group))

        print('\nСоздаю {} новых игр...'.format(games_cnt))
        for i in range(games_cnt):
            quiz = Quiz.objects.all().order_by('?').first()
            group = Group.objects.order_by('?').first()
            label = 'Test game #{}'.format(i)
            try:
                game = Game.objects.new_game(quiz, quiz.user, label, False, group)
                print('{}/{} Создана новая игра {}'.format(i + 1, games_cnt, game))
            except Exception:
                traceback.print_exc()
                print('Ошибка при добавлении {}'.format(label))

        print('\nСоздаю {} новых игроков...'.format(players_cnt))
        for i in range(players_cnt):
            game = Game.objects.all().order_by('?').first()
            user = User.objects.filter(email__contains='@test.ru').exclude(players__game=game).order_by('?').first()
            try:
                player = game.join(user)
                print('{}/{} Добавлен новый игрок {} в игру {}'.format(i + 1, players_cnt, player, game))
            except Exception:
                traceback.print_exc()
                print('Ошибка при добавлении {} в {}'.format(user, game))

