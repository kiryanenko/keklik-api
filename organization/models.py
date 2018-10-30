from django.db import models, transaction

from api.models import User


class OrganizationManager(models.Manager):
    @transaction.atomic
    def create_organization(self, name, user):
        organization = self.create(name=name)
        Admin.objects.create(organization=organization, user=user)
        return organization


class Organization(models.Model):
    name = models.CharField(max_length=300)

    objects = OrganizationManager()


class Admin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='admins')


class Group(models.Model):
    name = models.CharField(max_length=300)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='groups')


class GroupMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members')

    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
