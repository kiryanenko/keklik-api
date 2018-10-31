from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'phone',
            'last_name', 'first_name', 'patronymic',
            'gender', 'birth_date',
            'rating'
        )
        read_only_fields = ('username', 'rating')


class GetUserSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate_username(self, value):
        try:
            self.user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise ValidationError('User not found.', code='not_found')

        return value

    def save(self, **kwargs):
        return self.user