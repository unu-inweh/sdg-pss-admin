from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import *



# Register your models here.
User = get_user_model()

admin.site.register(User)
admin.site.register(Target)
admin.site.register(Indicator)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(QuestionCategory)
admin.site.register(Question)
admin.site.register(QuestionCategoryType)
admin.site.register(QuestionType)
admin.site.register(SdgComponents)
admin.site.register(Result)
admin.site.register(Team, TeamAdmin)
admin.site.register(TeamSummaryView, TeamSummaryViewAdmin)