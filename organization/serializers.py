from rest_framework import serializers

from organization.models import Organization, Group


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        return Group.objects.create(organization=self.context['organization'], **validated_data)


class OrganizationSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = Organization
        fields = ('id', 'name', 'groups', 'created_at', 'updated_at')
        read_only_fields = ('groups', 'created_at', 'updated_at')

    def create(self, validated_data):
        return Organization.objects.create_organization(validated_data.get('name'), self.context['request'].user)
