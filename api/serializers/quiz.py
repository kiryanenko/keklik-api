from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import Variant, Question, Tag, Quiz
from api.serializers.user import UserSerializer
from api.utils.serializers import CreatableSlugRelatedField


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

    def validate(self, attrs):
        answer = attrs.get('answer')
        variants = attrs.get('variants')

        for ans in answer:
            if ans > len(variants) or ans < 1:
                raise ValidationError(detail='Answer elements should be in 1..count_of_variants.')

        return attrs


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
