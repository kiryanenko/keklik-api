from rest_framework import serializers


class StatsSerializer(serializers.Serializer):
    users_count = serializers.IntegerField()
    games_count = serializers.IntegerField()
    organizations_count = serializers.IntegerField()
    groups_count = serializers.IntegerField()
    quizzes_count = serializers.IntegerField(help_text='Количество шаблонов викторин.')
