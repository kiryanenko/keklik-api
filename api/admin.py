from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from api.models import User, Quiz, Question, Variant, Tag, Game, GeneratedQuestion, Player, Answer

admin.site.register(User, UserAdmin)

admin.site.register(Question)
admin.site.register(Variant)
admin.site.register(Tag)

admin.site.register(Player)
admin.site.register(Answer)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    fields = ('title', 'description', 'user', 'tags', 'rating', 'version_date', 'old_version')
    readonly_fields = ('version_date',)
    list_display = ('title', 'description', 'user', 'rating', 'version_date', 'old_version')
    list_filter = ('tags', 'version_date')
    date_hierarchy = 'version_date'
    search_fields = ('title', 'description', 'tags')
    ordering = ('-version_date', '-id')
    raw_id_fields = ('old_version', 'user',)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    fields = ('label', 'quiz', 'online', 'state', 'current_question', 'user', 'organization', 'group',
              'created_at', 'state_changed_at', 'finished_at')
    readonly_fields = ('organization', 'created_at', 'state_changed_at', 'finished_at')
    list_display = ('label', 'quiz', 'online', 'state', 'current_question', 'user', 'organization', 'group',
                    'created_at', 'state_changed_at', 'finished_at')
    list_select_related = ('quiz', 'user', 'group__organization', 'current_question')
    list_filter = ('online', 'state', 'created_at')
    date_hierarchy = 'created_at'
    search_fields = ('label', 'quiz__title')
    ordering = ('-created_at', '-id')
    raw_id_fields = ('quiz', 'user', 'group', 'current_question')

    def organization(self, obj):
        if not obj.group:
            return None
        return obj.group.organization

    organization.short_description = 'Организация'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "car":
            pass
            # kwargs["queryset"] = Car.objects.filter(owner=request.user)
        return super(GameAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(GeneratedQuestion)
class GeneratedQuestionAdmin(admin.ModelAdmin):
    fields = ('question', 'game', 'variants_order', 'started_at')
    list_display = ('question', 'game', 'variants_order', 'started_at')
    list_filter = ('game__created_at',)
    date_hierarchy = 'game__created_at'
    search_fields = ('question',)
    ordering = ('-id',)
    raw_id_fields = ('question', 'game')
