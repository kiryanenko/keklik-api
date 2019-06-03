from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from api.models import User, Quiz, Question, Variant, Tag, Game, GeneratedQuestion, Player, Answer

admin.site.register(User, UserAdmin)

admin.site.register(Variant)
admin.site.register(Tag)

admin.site.register(Player)
admin.site.register(Answer)


class QuestionInline(admin.StackedInline):
    model = Question
    fields = ('question', 'number', 'type', 'answer', 'timer', 'points')
    ordering = ('number', 'id')
    extra = 1


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

    inlines = [
        QuestionInline
    ]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fields = ('question', 'number', 'type', 'quiz', 'answer', 'timer', 'points')
    list_display = ('question', 'number', 'type', 'quiz', 'points')
    list_filter = ('type', 'quiz__tags', 'quiz__version_date')
    date_hierarchy = 'quiz__version_date'
    search_fields = ('question', 'number', 'title', 'description', 'tags')
    ordering = ('-quiz', 'number', 'id')
    raw_id_fields = ('quiz',)


class GeneratedQuestionInline(admin.TabularInline):
    model = GeneratedQuestion
    fields = ('question', 'variants_order', 'started_at')
    readonly_fields = ('question', 'started_at')
    ordering = ('question__number', 'question__id')
    extra = 0


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

    inlines = [
        GeneratedQuestionInline
    ]

    def organization(self, obj):
        if not obj.group:
            return None
        return obj.group.organization

    organization.short_description = 'Организация'


@admin.register(GeneratedQuestion)
class GeneratedQuestionAdmin(admin.ModelAdmin):
    fields = ('question', 'game', 'variants_order', 'started_at')
    list_display = ('question', 'game', 'variants_order', 'started_at')
    list_filter = ('game__created_at',)
    date_hierarchy = 'game__created_at'
    search_fields = ('question',)
    ordering = ('game', 'question__number', 'id',)
    raw_id_fields = ('question', 'game')
