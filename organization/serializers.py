from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import User
from api.serializers.user import UserSerializer, GetUserSerializer
from organization.models import Organization, Group, Admin, GroupMember


class GroupMemberSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all(), help_text='Username')

    class Meta:
        model = GroupMember
        fields = ('user', 'role', 'created_at')
        read_only_fields = ('created_at',)

    def validate_user(self, value):
        group = self.context['group']
        if group.members.filter(user=value).exists():
            raise ValidationError('User is already in this group.', code='exists')

        return value

    def create(self, validated_data):
        return GroupMember.objects.create(group=self.context['group'], **validated_data)


class GroupSerializer(serializers.ModelSerializer):
    members = GroupMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'members', 'created_at', 'updated_at')
        read_only_fields = ('members', 'created_at', 'updated_at')

    def create(self, validated_data):
        return Group.objects.create(organization=self.context['organization'], **validated_data)


class AddAdminSerializer(GetUserSerializer):
    def validate_username(self, value):
        username = super().validate_username(value)

        organization = self.context['organization']
        if organization.admins.filter(user=self.user).exists():
            raise ValidationError('User is already admin in this organization.', code='exists')

        return username

    def save(self, **kwargs):
        user = super().save()
        organization = self.context['organization']
        return Admin.objects.create(organization=organization, user=user)


class DeleteAdminSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate_username(self, value):
        organization = self.context['organization']
        try:
            self.admin = organization.admins.get(user__username=value)
        except Admin.DoesNotExist:
            raise ValidationError('Admin not found.', code='not_found')

        return value

    def save(self, **kwargs):
        self.admin.delete()


class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Admin
        fields = ('user', 'created_at')


class OrganizationDetailSerializer(serializers.ModelSerializer):
    admins = AdminSerializer(many=True, read_only=True)
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = Organization
        fields = ('id', 'name', 'admins', 'groups', 'created_at', 'updated_at')
        read_only_fields = ('admins', 'groups', 'created_at', 'updated_at')

    def create(self, validated_data):
        return Organization.objects.create_organization(validated_data.get('name'), self.context['request'].user)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class OrganisationGroupSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()

    class Meta:
        model = Group
        fields = ('id', 'name', 'organization', 'created_at', 'updated_at')
        read_only_fields = ('organization', 'created_at', 'updated_at')

    def create(self, validated_data):
        return Group.objects.create(organization=self.context['organization'], **validated_data)


class MemberOfGroupSerializer(serializers.ModelSerializer):
    group = OrganisationGroupSerializer()

    class Meta:
        model = GroupMember
        fields = ('group', 'role', 'created_at')