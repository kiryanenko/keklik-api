from django.contrib import admin

from organization.models import Organization, Admin, Group, GroupMember

admin.site.register(Organization)
admin.site.register(Admin)
admin.site.register(Group)
admin.site.register(GroupMember)
