#from django.contrib.auth.models import User
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from pss_app.models import *
from django.core.mail import send_mail
User = get_user_model()

class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ('id', 'email', 'username', 'last_name', 'first_name', 'password', 'role', 'team', 'organization')
        ref_name = 'PssUserRegistration'

    def create(self, validated_data):
        # Check if email already exists
        email = validated_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                'email': 'A user with this email address already exists. Please use a different email or contact support if you forgot your username.'
            })

        # NationalTeamMember = 1
        # GenericUser = 2
        user = User.objects.create_user(**validated_data)
        user.is_active = False
        if(validated_data['role']==2):#GenereicUser gets active on registration
            user.is_active = True
            user.can_edit= True
        user.save()
        if (validated_data['role'] == 1):#NationalTeamMember needs approval from counry focal point
            team = validated_data['team']
            country_fp = User.objects.filter(team__id=team.id, country_focal_point=1)
            from_email = 'adpc.pss@gmail.com'
            #from_email='testeranon12@gmail.com'
            #to_emails = [from_email,'sdgpss@unu.edu']
            to_emails=[from_email]
            for c in country_fp:
                if c.email:
                    to_emails.append(c.email)
            #send_mail('New User Registered', 'Dear sir/madam,\n\nThe user ​'+str(user)+'​ requested access to SDG-PSS of ​'+str(team)+'. Please, click on the link below to confirm the user’s access. \n\nhttp://www.sdgpss.net/user-approval/confirm/'+str(user.id), from_email, to_emails, fail_silently=False)
            send_mail('New User Registered',
                      'Dear sir/madam,\n\nThe user ​' + str(user) + '​ requested access to SDG-PSS of ​' + str(team) +
                      '. Please, click on the link below to confirm the user\'s access. \n\nhttps://sdgpss-inweh.unu.edu/en/user-approval/confirm/' + str(user.id),
                      from_email, to_emails, fail_silently=False)
        return user

class UserSerializer(serializers.HyperlinkedModelSerializer):
    team_name = serializers.CharField(source='team.name', required=False)
    class Meta:
        model = User
        fields = ('id', 'username', 'email','role','team','team_name','last_name', 'first_name', 'organization', 'is_active', 'can_edit', 'country_focal_point')
        extra_kwargs = {'password' : {'write_only': True, 'required': True}}
        ref_name = 'PssUser'

    def update(self, instance, validated_data):
        # Send email after focal point member approves registration request
        if validated_data['is_active']==True and instance.is_active==False:
            print("in active====")
            from_email = 'adpc.pss@gmail.com'
            #from_email='testeranon12@gmail.com'
            to_emails = [from_email,instance.email]
            send_mail('Registration Approved',
                      "Dear sir/madam,\n\nYour registration to the SDG-PSS was approved by the national focal point of ​" + str(
                          instance.team) + "​ . You can access the system by clicking in the following link: ​ https://sdgpss-inweh.unu.edu/en/",
                      from_email, to_emails, fail_silently=False)
            #send_mail('Registration Approved',"Dear sir/madam,\n\nYour registration to the SDG-PSS was approved by the national focal point of ​"+str(instance.team)+"​ . You can access the system by clicking in the following link: ​ https://sdgpss.net/en/", from_email, to_emails, fail_silently=False)
        return super(UserSerializer, self).update(instance, validated_data)

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name')

class QuestionSerializer(serializers.ModelSerializer):
    question_type_name = serializers.CharField(source='question_type.name')
    order = serializers.IntegerField(source='question_type.order')
    default_option = serializers.IntegerField(source='question_type.default_option')
    default_value = serializers.CharField(source='question_type.default_value')
    question_type_required = serializers.CharField(source='question_type.required')
    question_type_percentage = serializers.CharField(source='question_type.percentage')
    question_type_non_zero = serializers.CharField(source='question_type.non_zero')
    question_type_numeric = serializers.CharField(source='question_type.numeric')
    class Meta:
        model = Question
        fields = ('id', 'question_text', 'question_text_fr', 'question_text_es','question_text_pt', 'question_text_ko','question_text_ar', 'question_type','question_type_name', 'order','question_grp', 'option1', 'option2', 'option3', 'option4', 'option5', 'option6',
                  'description','description_fr','description_es','description_pt', 'description_ko','description_ar', 'question_options', 'team', 'default_option', 'default_value', 'required', 'non_zero', 'percentage', 'numeric',
                  'question_type_required','question_type_percentage','question_type_non_zero','question_type_numeric', 'visible')

class QuestionSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'question_text', 'question_text_fr', 'question_text_es','question_text_pt', 'question_text_ko','question_text_ar', 'question_category','question_type', 'option1', 'option2', 'option3', 'option4', 'option5', 'option6', 'description','description_fr', 'description_es','description_pt','description_ko','description_ar', 'question_options', 'team', 'visible')

class QuestionCategorySerializer(serializers.ModelSerializer):
    question = QuestionSerializer(source='question_set',read_only=True, many=True)
    order = serializers.IntegerField(source='question_category_type.order')
    default_option = serializers.IntegerField(source='question_category_type.default_option')
    default_value = serializers.CharField(source='question_category_type.default_value')
    class Meta:
        model = QuestionCategory
        fields = ('id', 'name', 'name_fr', 'name_es','name_pt', 'name_ko','name_ar', 'question_type', 'question', 'option1', 'option2', 'option3', 'option4', 'option5', 'option6', 'order', 'description','description_fr','description_es','description_pt', 'description_ko','description_ar', 'itself_question','default_option', 'default_value', 'visible')

class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicator
        fields = ('id', 'label_id', 'name', 'name_fr', 'name_ko','name_ar', 'name_es','name_pt', 'order', 'description','description_fr', 'description_es','description_pt', 'description_ko', 'description_ar')

class TargetSerializer(serializers.ModelSerializer):
    indicator = IndicatorSerializer(source='indicator_set',read_only=True, many=True)
    class Meta:
        model = Target
        fields = ('id', 'label_id', 'name', 'name_fr', 'name_ko','name_ar', 'name_es','name_pt', 'order', 'indicator', 'description','description_fr', 'description_es','description_pt', 'description_ko', 'description_ar')

class SubCategorySerializer(serializers.ModelSerializer):
    question_category = QuestionCategorySerializer(source='questioncategory_set',read_only=True, many=True)
    class Meta:
        model = SubCategory
        fields = ('id', 'label_id', 'name', 'name_fr', 'name_ko', 'name_ar' ,'name_es','name_pt', 'order', 'question_category', 'description','description_fr', 'description_es','description_pt', 'description_ko','description_ar')

class CategorySerializer(serializers.ModelSerializer):
    sub_category = SubCategorySerializer(source='subcategory_set',read_only=True, many=True)
    class Meta:
        model = Category
        fields = ('id', 'label_id', 'name', 'name_fr', 'name_ko','name_ar', 'name_es','name_pt', 'order', 'sub_category', 'description','description_fr', 'description_es','description_pt', 'description_ko','description_ar')

class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = ('id', 'name','order','display_text','question_category_type')

class QuestionCategoryTypeSerializer(serializers.ModelSerializer):
    question_type = QuestionTypeSerializer(source='questiontype_set',read_only=True, many=True)
    class Meta:
        model = QuestionCategoryType
        fields = ('id', 'name', 'question_type','order','average','positive_response_percent','category_group','display_text', 'aggregate_title')

class ComponenetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(source='category_set',read_only=True, many=True)
    question_category_type = QuestionCategoryTypeSerializer(source='questioncategorytype_set', read_only=True,
                                                            many=True)
    class Meta:
        model = SdgComponents
        fields = ('id', 'name', 'category','question_category_type')

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ('user', 'team', 'question_category_type', 'question_type', 'question', 'question_category', 'sub_category', 'category', 'component', 'value', 'value_weight', 'display_value','question_grp','is_partial')

class ResultDataSerializer(serializers.ModelSerializer):
    question_category_type_name = serializers.CharField(source='question_category_type.name')
    question_category_group = serializers.CharField(source='question_category_type.category_group')
    question_type_name = serializers.CharField(source='question_type.name')
    class Meta:
        model = Result
        fields = ('user', 'team', 'question_category_type','question_category_type_name', 'question_type','question_type_name', 'question', 'question_category', 'sub_category', 'category', 'component', 'value', 'value_weight', 'display_value', 'question_category_group', 'is_partial', 'last_saved')

class ReportResultSerializer(serializers.ModelSerializer):
    question_category_type = serializers.CharField(source='question_category_type.name')
    question_type = serializers.CharField(source='question_type.name')
    category_name = serializers.CharField(source='category.name')
    sub_category_name = serializers.CharField(source='sub_category.name')
    category_order = serializers.CharField(source='category.order')
    sub_category_order = serializers.CharField(source='sub_category.order')
    question_type_order = serializers.CharField(source='question_type.order')
    question_category_type_order = serializers.CharField(source='question_category_type.order')
    question_type_display = serializers.CharField(source='question_type.display_text')
    class Meta:
        model = Result
        fields = ('user', 'team', 'question_category_type', 'question_type', 'question', 'question_category', 'sub_category', 'category', 'component', 'value', 'value_weight', 'display_value', 'category_name', 'sub_category_name',
                  'category_order', 'sub_category_order','question_type_order','question_category_type_order','question_type_display', 'question_grp')

# Summary Related Serializers
class SummaryComponenetSerial(serializers.ModelSerializer):
    class Meta:
        model = SdgComponents
        fields = ('id', 'name')

class SummaryQuestionCategoryTypeSerializer(serializers.ModelSerializer):
    component = SummaryComponenetSerial()
    class Meta:
        model = QuestionCategoryType
        fields = ('id', 'name','component','average','positive_response_percent','category_group','display_text')

class SummaryQuestionTypeSerializer(serializers.ModelSerializer):
    question_category_type = SummaryQuestionCategoryTypeSerializer()
    class Meta:
        model = QuestionType
        fields = ('id', 'name','order','display_text','question_category_type')

class TeamSummaryColumnSerializer(serializers.ModelSerializer):
    question_category_type = SummaryQuestionCategoryTypeSerializer()
    question_type = SummaryQuestionTypeSerializer()
    class Meta:
        model = TeamSummaryView
        fields = ('id', 'display_text', 'question_type','question_category_type','team','show_in_summary')

class TeamSummarySubCategorySerializer(serializers.ModelSerializer):
    label_id = serializers.SerializerMethodField() 

    def get_label_id(self, obj):
        return obj.label_id[1:]
    
    class Meta:
        model = SubCategory
        fields = ('label_id', 'name', 'order')

class TeamSummaryRowSerializer(serializers.ModelSerializer):
    label_id = serializers.SerializerMethodField() 
    sub_category = TeamSummarySubCategorySerializer(source='subcategory_set',read_only=True, many=True)
    
    def get_label_id(self, obj):
        return obj.label_id[1:]
    
    class Meta:
        model = Category
        fields = ('label_id', 'name', 'order', 'sub_category')

class TeamSummaryResultSerializer(serializers.ModelSerializer):
    question_category_type_name = serializers.CharField(source='question_category_type.name')
    question_category_group = serializers.CharField(source='question_category_type.category_group')
    question_type_name = serializers.CharField(source='question_type.name')
    sub_category = serializers.CharField(source='sub_category.label_id')
    class Meta:
        model = Result
        fields = ('team', 'question_category_type','question_category_type_name', 'question_type','question_type_name', 'question', 'question_category', 'sub_category', 'category', 'component', 'value', 'value_weight', 'display_value', 'question_category_group')