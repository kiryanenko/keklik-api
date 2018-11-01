from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from api.models import User, Quiz, Question, Variant, Tag, Game, GeneratedQuestion, Player, Answer

admin.site.register(User, UserAdmin)

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Variant)
admin.site.register(Tag)

admin.site.register(Game)
admin.site.register(GeneratedQuestion)
admin.site.register(Player)
admin.site.register(Answer)
