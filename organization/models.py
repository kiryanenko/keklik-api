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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='admins')
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('organization', 'user')

    def __str__(self):
        return str(self.user)


class Group(models.Model):
    name = models.CharField(max_length=300)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class GroupMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='member_of_groups')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members')
    created_at = models.DateTimeField(auto_now=True)

    STUDENT_ROLE = 'student'
    TEACHER_ROLE = 'teacher'
    ROLE_CHOICES = (
        (STUDENT_ROLE, 'Student'),
        (TEACHER_ROLE, 'Teacher'),
    )
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('group', 'user', 'role')

    @property
    def organization(self):
        return self.group.organization

    def __str__(self):
        return str(self.user)
