from rest_framework import serializers

from api.models import User
from organization.serializers import MemberOfGroupSerializer


class UserDetailSerializer(serializers.ModelSerializer):

    member_of_groups = MemberOfGroupSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'phone',
            'last_name', 'first_name', 'patronymic',
            'gender', 'birth_date',
            'rating', 'member_of_groups'
        )
        read_only_fields = ('username', 'rating', 'member_of_groups')
