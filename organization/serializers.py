from rest_framework import serializers

from organization.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name')

    def create(self, validated_data):
        return Organization.objects.create_organization(validated_data.get('name'), self.context['request'].user)
