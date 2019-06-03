from django.contrib import admin

from organization.models import Organization, Admin, Group, GroupMember

admin.site.register(Admin)
admin.site.register(Group)
admin.site.register(GroupMember)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    fields = ('name', 'quizzes', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('name', 'created_at')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    search_fields = ('name',)
    ordering = ('-created_at', 'name')
    raw_id_fields = ('quizzes',)
