from __future__ import unicode_literals
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from django.contrib import admin

class User(AbstractUser):
    NationalTeamMember = 1
    GenericUser = 2
    ROLE_CHOICES = (
        (NationalTeamMember, 'National Team Member'),
        (GenericUser, 'Generic User')
    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=True, blank=True)
    team = models.ForeignKey('Team', on_delete=models.CASCADE, null=True, blank=True)
    organization = models.CharField(max_length=50,blank=True, null=True)
    can_edit = models.BooleanField(default=False)
    country_focal_point = models.BooleanField(default=False)
    REQUIRED_FIELDS = ["email", "role", "team", "can_edit", "country_focal_point"]

class Team(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name

class TeamAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        if(change == False):
            TeamSummaryView.objects.create(question_category_type=QuestionCategoryType.objects.get(id=46), team=obj, show_in_summary=True, display_text="Strategies")
            TeamSummaryView.objects.create(question_category_type=QuestionCategoryType.objects.get(id=49), team=obj, show_in_summary=True, display_text="Information and Assessments")
            TeamSummaryView.objects.create(question_category_type=QuestionCategoryType.objects.get(id=54), team=obj, show_in_summary=True, display_text="Infra-structure")
            TeamSummaryView.objects.create(question_category_type=QuestionCategoryType.objects.get(id=68), team=obj, show_in_summary=True, display_text="Policy and Integrity")
            TeamSummaryView.objects.create(question_category_type=QuestionCategoryType.objects.get(id=69), team=obj, show_in_summary=True, display_text="Regulatory Policy")
            TeamSummaryView.objects.create(question_category_type=QuestionCategoryType.objects.get(id=70), team=obj, show_in_summary=True, display_text="Development Cooperation")
            TeamSummaryView.objects.create(question_category_type=QuestionCategoryType.objects.get(id=71), team=obj, show_in_summary=True, display_text="Public Sector Integrity")
            TeamSummaryView.objects.create(question_category_type=QuestionCategoryType.objects.get(id=72), team=obj, show_in_summary=True, display_text="Whistle-blower Protection")
            TeamSummaryView.objects.create(question_category_type=QuestionCategoryType.objects.get(id=30), team=obj, show_in_summary=True, display_text="Adequacy of financial flows")
            TeamSummaryView.objects.create(question_category_type=QuestionCategoryType.objects.get(id=32), team=obj, show_in_summary=True, display_text="Accounta-bility")
            TeamSummaryView.objects.create(question_category_type=QuestionCategoryType.objects.get(id=37), team=obj, show_in_summary=True, display_text="Funding Sources")
            TeamSummaryView.objects.create(question_category_type=QuestionCategoryType.objects.get(id=39), team=obj, show_in_summary=True, display_text="Financing for equity")
            TeamSummaryView.objects.create(question_category_type=QuestionCategoryType.objects.get(id=10), team=obj, show_in_summary=True, display_text="Policy for equity")
            TeamSummaryView.objects.create(question_category_type=QuestionCategoryType.objects.get(id=12), team=obj, show_in_summary=True, display_text="Coordination & cooperation")
            TeamSummaryView.objects.create(question_type=QuestionType.objects.get(id=186), team=obj, show_in_summary=True, display_text="Awareness")
            TeamSummaryView.objects.create(question_type=QuestionType.objects.get(id=245), team=obj, show_in_summary=True, display_text="National policy")
            TeamSummaryView.objects.create(question_type=QuestionType.objects.get(id=253), team=obj, show_in_summary=True, display_text="Governance")
            TeamSummaryView.objects.create(question_type=QuestionType.objects.get(id=265), team=obj, show_in_summary=True, display_text="Organisation main-streaming")
            TeamSummaryView.objects.create(question_type=QuestionType.objects.get(id=11), team=obj, show_in_summary=True, display_text="Overall current capacity")
            TeamSummaryView.objects.create(question_category_type=QuestionCategoryType.objects.get(id=2), team=obj, show_in_summary=True, display_text="Strength-ening mechanisms")
            TeamSummaryView.objects.create(question_category_type=QuestionCategoryType.objects.get(id=3), team=obj, show_in_summary=True, display_text="Overall Progress")
        return super(TeamAdmin, self).save_model(request, obj, form, change)

class Result(models.Model):
    team = models.ForeignKey('Team', on_delete=models.CASCADE, null=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    question_category = models.ForeignKey('QuestionCategory', on_delete=models.CASCADE)
    sub_category = models.ForeignKey('SubCategory', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    component = models.ForeignKey('SdgComponents', on_delete=models.CASCADE)
    question_category_type = models.ForeignKey('QuestionCategoryType', on_delete=models.CASCADE)
    question_type = models.ForeignKey('QuestionType', on_delete=models.CASCADE)
    question_grp = models.IntegerField(null=True)
    value = models.CharField(max_length=255, db_index=True, blank=True)
    value_weight = models.IntegerField()
    display_value = models.CharField(max_length=255, null=True, blank=True)
    is_partial = models.BooleanField(default=False)
    last_saved = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.question)+self.value

class SdgComponents(models.Model):
    label_id = models.CharField(max_length=20, blank=True,null=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.label_id + self.name
    
    
    

class Target(models.Model):
    label_id = models.CharField(max_length=20,blank=True, null=True)
    name = models.CharField(max_length=500)
    name_fr = models.CharField(max_length=500,blank=True, null=True)
    name_es = models.CharField(max_length=500,blank=True, null=True)
    name_pt = models.CharField(max_length=500,blank=True, null=True)
    name_ko = models.CharField(max_length=500,blank=True, null=True)
    name_ar = models.CharField(max_length=500, blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=1)
    description = models.CharField(max_length=2000, blank=True, null=True)
    description_fr = models.CharField(max_length=2000, blank=True, null=True)
    description_es = models.CharField(max_length=2000, blank=True, null=True)
    description_pt = models.CharField(max_length=2000, blank=True, null=True)
    description_ko = models.CharField(max_length=2000, blank=True, null=True)
    description_ar = models.CharField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.label_id + self.name

class Indicator(models.Model):
    label_id = models.CharField(max_length=20, blank=True,null=True)
    name = models.CharField(max_length=500)
    name_fr = models.CharField(max_length=500,blank=True, null=True)
    name_es = models.CharField(max_length=500,blank=True, null=True)
    name_pt = models.CharField(max_length=500, blank=True, null=True)
    name_ko = models.CharField(max_length=500,blank=True, null=True)
    name_ar = models.CharField(max_length=500, blank=True, null=True)
    target = models.ForeignKey('Target', on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=1)
    description = models.CharField(max_length=2000, blank=True, null=True)
    description_fr = models.CharField(max_length=2000, blank=True, null=True)
    description_es = models.CharField(max_length=2000, blank=True, null=True)
    description_pt = models.CharField(max_length=2000, blank=True, null=True)
    description_ko = models.CharField(max_length=2000, blank=True, null=True)
    description_ar = models.CharField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.label_id + self.name

class Category(models.Model):
    label_id = models.CharField(max_length=20,blank=True, null=True)
    name = models.CharField(max_length=500)
    name_fr = models.CharField(max_length=500,blank=True, null=True)
    name_es = models.CharField(max_length=500,blank=True, null=True)
    name_pt = models.CharField(max_length=500, blank=True, null=True)
    name_ko = models.CharField(max_length=500,blank=True, null=True)
    name_ar = models.CharField(max_length=500, blank=True, null=True)
    component = models.ForeignKey('SdgComponents', on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=1)
    description = models.CharField(max_length=2000, blank=True, null=True)
    description_fr = models.CharField(max_length=2000, blank=True, null=True)
    description_es = models.CharField(max_length=2000, blank=True, null=True)
    description_pt = models.CharField(max_length=2000, blank=True, null=True)
    description_ko = models.CharField(max_length=2000, blank=True, null=True)
    description_ar = models.CharField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.label_id + self.name

class SubCategory(models.Model):
    label_id = models.CharField(max_length=20, blank=True,null=True)
    name = models.CharField(max_length=500)
    name_fr = models.CharField(max_length=500,blank=True, null=True)
    name_es = models.CharField(max_length=500,blank=True, null=True)
    name_pt = models.CharField(max_length=500, blank=True, null=True)
    name_ko = models.CharField(max_length=500,blank=True, null=True)
    name_ar = models.CharField(max_length=500, blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=1)
    description = models.CharField(max_length=2000, blank=True, null=True)
    description_fr = models.CharField(max_length=2000, blank=True, null=True)
    description_es = models.CharField(max_length=2000, blank=True, null=True)
    description_pt = models.CharField(max_length=2000, blank=True, null=True)
    description_ko = models.CharField(max_length=2000, blank=True, null=True)
    description_ar = models.CharField(max_length=2000, blank=True, null=True)
    def __str__(self):
        return self.label_id + self.name

class QuestionCategory(models.Model):
    TYPE_CHOICES = (
        ('CheckBox', 'CheckBox'),
        ('Slider', 'Slider'),
        ('TextField', 'TextField'),
        ('NumberField', 'NumberField'),
        ('RadioButtons', 'RadioButtons'),
        ('RadioButtons3', 'RadioButtons3'),
        ('Tabular', 'Tabular'),
        ('Radetail1', 'Radetail1'),
        ('Radetail2', 'Radetail2'),
        ('Radother', 'Radother'),
        ('Empty', 'Empty')
    )
    label_id = models.CharField(max_length=20, blank=True,null=True)
    question_type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    name = models.CharField(max_length=500)
    name_fr = models.CharField(max_length=500,blank=True, null=True)
    name_es = models.CharField(max_length=500,blank=True, null=True)
    name_pt = models.CharField(max_length=500, blank=True, null=True)
    name_ko = models.CharField(max_length=500,blank=True, null=True)
    name_ar = models.CharField(max_length=500, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    description_fr = models.CharField(max_length=1000, blank=True, null=True)
    description_es = models.CharField(max_length=1000, blank=True, null=True)
    description_pt = models.CharField(max_length=2000, blank=True, null=True)
    description_ko = models.CharField(max_length=1000, blank=True, null=True)
    description_ar = models.CharField(max_length=1000, blank=True, null=True)
    itself_question = models.BooleanField(default=False)
    sub_category = models.ForeignKey('SubCategory', on_delete=models.CASCADE)
    question_category_type = models.ForeignKey('QuestionCategoryType', on_delete=models.CASCADE, blank=True, null=True)
    option1 = models.CharField(max_length=100, blank=True, null=True)
    option2 = models.CharField(max_length=100, blank=True, null=True)
    option3 = models.CharField(max_length=100, blank=True, null=True)
    option4 = models.CharField(max_length=100, blank=True, null=True)
    option5 = models.CharField(max_length=100, blank=True, null=True)
    option6 = models.CharField(max_length=100, blank=True, null=True)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return self.label_id + self.name

class Question(models.Model):
    label_id = models.CharField(max_length=20, blank=True,null=True)
    question_text = models.CharField(max_length=500)
    question_text_fr = models.CharField(max_length=500,blank=True, null=True)
    question_text_es = models.CharField(max_length=500,blank=True, null=True)
    question_text_pt = models.CharField(max_length=500,blank=True, null=True)
    question_text_ko = models.CharField(max_length=500,blank=True, null=True)
    question_text_ar = models.CharField(max_length=500, blank=True, null=True)
    question_category = models.ForeignKey('QuestionCategory', on_delete=models.CASCADE)
    question_type = models.ForeignKey('QuestionType', on_delete=models.CASCADE, blank=True, null=True )
    question_grp = models.IntegerField(blank=True, null=True)
    option1 = models.CharField(max_length=100, blank=True, null=True)
    option2 = models.CharField(max_length=100, blank=True, null=True)
    option3 = models.CharField(max_length=100, blank=True, null=True)
    option4 = models.CharField(max_length=100, blank=True, null=True)
    option5 = models.CharField(max_length=100, blank=True, null=True)
    option6 = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    description_fr = models.CharField(max_length=1000, blank=True, null=True)
    description_es = models.CharField(max_length=1000, blank=True, null=True)
    description_pt = models.CharField(max_length=1000, blank=True, null=True)
    description_ko = models.CharField(max_length=1000, blank=True, null=True)
    description_ar = models.CharField(max_length=1000, blank=True, null=True)
    result_unit = models.CharField(max_length=100, blank=True, null=True)
    team = models.ForeignKey('Team', on_delete=models.CASCADE, blank=True, null=True )
    TYPE_CHOICES = (
        ('1', 'Input'),
        ('2', 'RadioButton2'),
        ('3', 'RadioButton3'),
        ('4', 'RadioButton4')
    )
    question_options = models.CharField(max_length=100, choices=TYPE_CHOICES, blank=True, null=True)
    required = models.BooleanField(default=False)
    non_zero = models.BooleanField(default=False)
    percentage = models.BooleanField(default=False)
    numeric = models.BooleanField(default=False)
    visible = models.BooleanField(default=True)

    def __str__(self):
        if(self.question_grp and self.label_id):
            return self.label_id + self.question_text + ' Group:' + str(self.question_grp)
        else:
            return self.question_text

class QuestionCategoryType(models.Model):
    label_id = models.CharField(max_length=20, blank=True,null=True)
    name = models.CharField(max_length=500)
    component = models.ForeignKey('SdgComponents', on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=1)
    average = models.BooleanField(default=False)
    positive_response_percent = models.BooleanField(default=False)
    aggregate_title = models.CharField(max_length=500, blank=True, null=True)
    category_group = models.CharField(max_length=255, blank=True, null=True)
    display_text = models.CharField(max_length=255, blank=True, null=True)
    default_option = models.IntegerField(default=0)
    default_value = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

class QuestionType(models.Model):
    label_id = models.CharField(max_length=20, blank=True,null=True)
    name = models.CharField(max_length=500)
    question_category_type = models.ForeignKey('QuestionCategoryType', on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=1)
    display_text = models.CharField(max_length=255, blank=True, null=True)
    show_in_summary = models.BooleanField(default=False)
    default_option = models.IntegerField(default=0)
    default_value = models.CharField(max_length=255, blank=True, null=True)
    required = models.BooleanField(default=False)
    non_zero = models.BooleanField(default=False)
    percentage = models.BooleanField(default=False)
    numeric = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class TeamSummaryView(models.Model):
    question_type = models.ForeignKey('QuestionType', on_delete=models.CASCADE, blank=True, null=True, limit_choices_to={'show_in_summary': True} )
    question_category_type = models.ForeignKey('QuestionCategoryType', on_delete=models.CASCADE, blank=True, null=True, limit_choices_to=Q(average=True) | Q(positive_response_percent=True) )
    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    show_in_summary = models.BooleanField(default=False)
    display_text = models.CharField(max_length=50, blank=True, null=True)

class TeamSummaryListFilter(admin.SimpleListFilter):
    title = 'team'
    parameter_name = 'team'
    def lookups(self, request, model_admin):
        return (
            ('80s', 'in the eighties'),
            ('90s', 'in the nineties'),
        )

    def queryset(self, request, queryset):
        return queryset

class TeamSummaryViewAdmin(admin.ModelAdmin):
    list_display = ('display_text', 'question_type', 'question_category_type', 'team', 'show_in_summary')
    list_filter = (
        ('team', admin.RelatedOnlyFieldListFilter),
        ('show_in_summary')
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        team = request.user.team
        return qs.filter(team=team)