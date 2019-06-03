from django.contrib import admin

from organization.models import Organization, Admin, Group, GroupMember

admin.site.register(Group)
admin.site.register(GroupMember)


class OrganizationAdminInline(admin.TabularInline):
    model = Admin
    fields = ('user', 'created_at',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at', 'user')
    raw_id_fields = ('user',)
    show_change_link = True
    extra = 0


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

    inlines = [
        OrganizationAdminInline
    ]


@admin.register(Admin)
class OrganizationAdminAdmin(admin.ModelAdmin):
    fields = ('user', 'organization', 'created_at',)
    readonly_fields = ('created_at',)
    list_display = ('user', 'organization', 'created_at',)
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    search_fields = ('user', 'organization')
    ordering = ('-created_at', 'user')
    raw_id_fields = ('user', 'organization',)

