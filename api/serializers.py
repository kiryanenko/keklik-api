from rest_framework import serializers

from api.models import User


class CredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(validated_data.get('username'), password=validated_data.get('password'))




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'password',
            'email', 'phone',
            'last_name', 'first_name', 'patronymic',
            'gender', 'birth_date'
        )
        read_only_fields = ('username',)
        extra_kwargs = {
            'password': {'write_only': True},
            # 'email': {'required': False},
            # 'phone': {'required': False},
            # 'last_name': {'required': False},
            # 'first_name': {'required': False},
            # 'patronymic': {'required': False},
            # 'gender': {'required': False},
            # 'birth_date': {'required': False}
        }
