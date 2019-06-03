from django.db import models, transaction

from api.models import User, Quiz


class OrganizationManager(models.Manager):
    @transaction.atomic
    def create_organization(self, name, user):
        organization = self.create(name=name)
        Admin.objects.create(organization=organization, user=user)
        return organization


class Organization(models.Model):
    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'

    name = models.CharField(verbose_name='Название', max_length=300)
    quizzes = models.ManyToManyField(Quiz, verbose_name='Викторины организации')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    objects = OrganizationManager()

    def __str__(self):
        return self.name


class Admin(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, verbose_name='Организация', on_delete=models.CASCADE,
                                     related_name='admins')
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата назначения')

    class Meta:
        verbose_name = 'Админ организации'
        verbose_name_plural = 'Админы организаций'
        unique_together = ('organization', 'user')

    def __str__(self):
        return str(self.user)


class Group(models.Model):
    class Meta:
        verbose_name = 'Группа организации'
        verbose_name_plural = 'Группы организаций'

    name = models.CharField(verbose_name='Название', max_length=300)
    organization = models.ForeignKey(Organization, verbose_name='Организация', on_delete=models.CASCADE,
                                     related_name='groups')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        return self.name


class GroupMember(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE,
                             related_name='member_of_groups')
    group = models.ForeignKey(Group, verbose_name='Группа организации', on_delete=models.CASCADE,
                              related_name='members')
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата добавления')

    STUDENT_ROLE = 'student'
    TEACHER_ROLE = 'teacher'
    ROLE_CHOICES = (
        (STUDENT_ROLE, 'Студент'),
        (TEACHER_ROLE, 'Учитель'),
    )
    role = models.CharField(choices=ROLE_CHOICES, verbose_name='Роль', max_length=100)

    class Meta:
        verbose_name = 'Член группы организации'
        verbose_name_plural = 'Члены групп организаций'
        unique_together = ('group', 'user', 'role')

    @property
    def organization(self):
        return self.group.organization

    def __str__(self):
        return str(self.user)
