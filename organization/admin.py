from django.contrib import admin

from organization.models import Organization, Admin, Group, GroupMember


class OrganizationAdminInline(admin.TabularInline):
    model = Admin
    fields = ('user', 'created_at',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at', 'user')
    raw_id_fields = ('user',)
    show_change_link = True
    extra = 0


class OrganizationGroupInline(admin.TabularInline):
    model = Group
    fields = ('name', 'organization', 'created_at',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at', 'name')
    show_change_link = True
    extra = 0


class OrganizationMemberInline(admin.TabularInline):
    model = GroupMember
    fields = ('user', 'role', 'created_at')
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
        OrganizationGroupInline,
        OrganizationAdminInline,
    ]


@admin.register(Admin)
class OrganizationAdminAdmin(admin.ModelAdmin):
    fields = ('user', 'organization', 'created_at',)
    readonly_fields = ('created_at',)
    list_display = ('user', 'organization', 'created_at',)
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    search_fields = ('user', 'organization')
    ordering = ('-organization', '-created_at', '-id')
    raw_id_fields = ('user', 'organization',)


@admin.register(Group)
class OrganizationGroupAdmin(admin.ModelAdmin):
    fields = ('name', 'organization', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('name', 'organization', 'created_at',)
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    search_fields = ('name', 'organization')
    ordering = ('-created_at', 'name')
    raw_id_fields = ('organization',)

    inlines = [
        OrganizationMemberInline
    ]


@admin.register(GroupMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    fields = ('user', 'organization', 'group', 'role', 'created_at')
    readonly_fields = ('organization', 'created_at',)
    list_display = ('user', 'organization', 'group', 'role', 'created_at',)
    list_filter = ('role', 'created_at',)
    date_hierarchy = 'created_at'
    search_fields = ('user', 'group')
    ordering = ('-group__organization', '-group', '-created_at', '-id')
    raw_id_fields = ('user', 'group',)

    def organization(self, obj):
        if not obj.group:
            return None
        return obj.group.organization

    organization.short_description = 'Организация'
