from rest_framework import serializers
from rest_framework.fields import empty

from organization.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    def __init__(self, user=None, data=empty, **kwargs):
        super().__init__(data=data, **kwargs)
        self.user = user

    class Meta:
        model = Organization
        fields = ('id', 'name')

    def create(self, validated_data):
        return Organization.objects.create_organization(validated_data.get('name'), self.user)
