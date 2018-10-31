from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import User
from organization.serializers import MemberOfGroupSerializer


class CredentialsSerializer(serializers.ModelSerializer):
    session_key = serializers.CharField(read_only=True)
    member_of_groups = MemberOfGroupSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'password', 'token', 'session_key',
            'email', 'phone',
            'last_name', 'first_name', 'patronymic',
            'gender', 'birth_date', 'member_of_groups'
        )
        read_only_fields = (
            'token', 'session_key',
            'email', 'phone',
            'last_name', 'first_name', 'patronymic',
            'gender', 'birth_date', 'member_of_groups'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'token': {'help_text': 'Токен аутентификации, который необходимо добавлять в заголовок\n'
                                   '"Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"'}
        }

    def create(self, validated_data):
        return User.objects.create_user(validated_data.get('username'), password=validated_data.get('password'))

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['session_key'] = self.context['request'].session.session_key
        return ret


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def update(self, instance, validated_data):
        instance.set_password(validated_data.get('new_password'))
        instance.save()
        return instance

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate_old_password(self, value):
        if not self.instance.check_password(value):
            raise ValidationError('Incorrect old password')
        return value


