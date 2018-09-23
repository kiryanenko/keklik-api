from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import User


class CredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(validated_data.get('username'), password=validated_data.get('password'))

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'phone',
            'last_name', 'first_name', 'patronymic',
            'gender', 'birth_date'
        )
        read_only_fields = ('username',)


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
