from django.contrib.auth import password_validation
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_text
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import User, Quiz, Question, Variant, Tag


class CreatableSlugRelatedField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(**{self.slug_field: data})[0]
        except ObjectDoesNotExist:
            self.fail('does_not_exist', slug_name=self.slug_field, value=smart_text(data))
        except (TypeError, ValueError):
            self.fail('invalid')


class CredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'password', 'token',
            'email', 'phone',
            'last_name', 'first_name', 'patronymic',
            'gender', 'birth_date'
        )
        read_only_fields = (
            'token',
            'email', 'phone',
            'last_name', 'first_name', 'patronymic',
            'gender', 'birth_date'
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


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ('id', 'variant',)


class QuestionSerializer(serializers.ModelSerializer):
    variants = VariantSerializer(many=True)

    class Meta:
        model = Question
        fields = ('id', 'number', 'type', 'question', 'variants', 'answer', 'timer', 'points')
        read_only_fields = ('number',)


class QuizSerializer(serializers.ModelSerializer):
    tags = CreatableSlugRelatedField(many=True, queryset=Tag.objects.all(), slug_field='tag')
    user = UserSerializer(read_only=True)
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = (
            'id', 'title', 'description',
            'user',
            'tags',
            'questions',
            'rating',
            'version_date'
        )
        read_only_fields = ('user', 'rating', 'version_date')

    def create(self, validated_data):
        return Quiz.objects.create_quiz(**validated_data)

    def update(self, instance, validated_data):
        return instance.update(**validated_data)
