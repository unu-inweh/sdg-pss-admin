#from django.contrib.auth.models import User
from rest_framework import viewsets,generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from pss_app.serializers import UserSerializer
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from .models import Result, QuestionCategoryType, QuestionType, TeamSummaryView
from .serializers import ResultSerializer
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from pss_app.models import *
from pss_app.serializers import *
from django.db.models import Q
from django.db import transaction
from django.core.mail import send_mail
from django.middleware.csrf import get_token
import logging
User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def feedback(request):
    send_mail(
        'Feedback Form submission',
        'Please take a look on the feedback.\n'
        'Full Name: ' + request.data["full_name"] + '\n'
        'Email: ' + request.data["email"] + '\n'
        'Country: ' + request.data["country"] + '\n'
        'Comment: ' + request.data["comment"],
        'adpc.pss@gmail.com',
        ['adpc.pss@gmail.com'],
        fail_silently=False
    )
    return Response("Successful")

@api_view(['GET'])
@permission_classes([AllowAny])
def getcsrf(request):
    csrf_token = get_token(request)
    return Response(csrf_token)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def team_members(request):
    team = request.query_params.get('team')
    queryset = User.objects.filter(team=team, country_focal_point=0)
    serializer = UserSerializer(queryset, many=True,context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def result1(request):
    comp = request.query_params.get('component')
    save_by = request.query_params.get('save_by')
    if (save_by == 'user'):
        print("save_by == 'user'")
        user = request.query_params.get('user')
        print(user)
        queryset = Result.objects.filter(user=user, component=comp)
        print('=====result1======')
        print(len(queryset))
    else:
        print("save_by == 'team'")
        team = request.query_params.get('team')
        print(team)
        queryset = Result.objects.filter(team=team, component=comp)
    serializer = ResultDataSerializer(queryset, many=True)
    return Response(serializer.data)

@transaction.atomic
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def result(request):
    saved = True
    if request.method == 'GET':
        comp = request.query_params.get('component')
        save_by = request.query_params.get('save_by')
        print(save_by)
        if (save_by == 'user'):
            print("save_by == 'user'")
            user = request.query_params.get('user')
            print(user)
            queryset = Result.objects.filter(user=user, component=comp).order_by('question_type', 'value')
            print('======result=======')
            print(len(queryset))
        else:
            print("save_by == 'team'")
            team = request.query_params.get('team')
            print(team)
            queryset = Result.objects.filter(team=team, component=comp).order_by('question_type', 'value')
        serializer = ReportResultSerializer(queryset, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        save_by = request.data['save_by']
        comp = request.data['component']
        data = request.data['data']
        is_partial = request.data['is_partial']
        if(save_by == 'user'):
            user = request.data['user']
            Result.objects.filter(user=user, component=comp).delete()
        else:
            team = request.data['team']
            Result.objects.filter(team=team, component=comp).delete()
        # questions = Question.objects.filter(Q(team=None) | Q(team=team),question_category__sub_category__category__component__id=comp).all()
        questions = Question.objects.filter(question_category__sub_category__category__component__id=comp).all()
        for question in questions:
            qid = str(question.id)
            if qid in data:
                data[qid]['question_category'] = question.question_category.id
                data[qid]['sub_category'] = question.question_category.sub_category.id
                data[qid]['category'] = question.question_category.sub_category.category.id
                data[qid]['component'] = question.question_category.sub_category.category.component.id
                data[qid]['question_category_type'] = question.question_category.question_category_type.id
                data[qid]['question_type'] = question.question_type.id
                data[qid]['question_grp'] = question.question_grp
                if (save_by == 'user'):
                    data[qid]['user'] = user
                else:
                    data[qid]['team'] = team
                data[qid]['is_partial'] = is_partial
                serializer = ResultSerializer(data=data[qid])
                if serializer.is_valid() and saved:
                    serializer.save()
                else:
                    saved = False
        if(saved):
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def team_summary_headings(request):
    team = request.query_params.get('team')
    qct_queryset = QuestionCategoryType.objects.filter(Q(average=True) | Q(positive_response_percent=True))
    qc_queryset = QuestionType.objects.filter(show_in_summary=True)
    tsch_queryset = TeamSummaryView.objects.filter(team=team, show_in_summary=True)
    tsrh_queryset = Category.objects.filter(component = 5) #Hard coding to get just one set
    target_queryset = Target.objects.all()

    qct_serializer = SummaryQuestionCategoryTypeSerializer(qct_queryset, many=True)
    qt_serializer = SummaryQuestionTypeSerializer(qc_queryset, many=True)
    tsch_serializer = TeamSummaryColumnSerializer(tsch_queryset, many=True)
    tsrh_serializer = TeamSummaryRowSerializer(tsrh_queryset, many=True)
    target_serializer = TargetSerializer(target_queryset, many=True)

    response = []
    response.append({"qct":qct_serializer.data})
    response.append({"qt":qt_serializer.data})
    response.append({"tsch":tsch_serializer.data})
    response.append({"tsrh":tsrh_serializer.data})
    response.append({"targets":target_serializer.data})
    return Response(response)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def team_summary_results(request):
    team = request.query_params.get('team')
    comp = request.query_params.get('component')
    user = request.query_params.get('user')
    save_by=request.query_params.get('save_by')
    if save_by == 'user':
        queryset = Result.objects.filter(user=user, component=comp).order_by('sub_category', 'question_type')
        print(queryset)
        print('========Userrrrrrrr=======')
        print('length of query set userrrr:', len(queryset))
        logging.warning(len(queryset))
        serializer = TeamSummaryResultSerializer(queryset, many=True)
        return Response(serializer.data)
    else:
        queryset = Result.objects.filter(team=team, component=comp).order_by('sub_category', 'question_type')
        print(queryset)
        print('========teamsummaryresult=======')
        print('length of query set :',len(queryset))
        logging.warning(len(queryset))
        serializer = TeamSummaryResultSerializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def add_question(request):
    question = request.data['question']
    team = request.data['team']
    que_cats = QuestionCategory.objects.filter(sub_category__category__component__id=question['component'], name='Pool Questions').all()
    que_types = QuestionType.objects.filter(question_category_type=que_cats[0].question_category_type.id).order_by('-order')
    data = {}
    quetype_data = {}
    order = None
    if (que_types):
        order = que_types[0].order+1
    else:
        order = 1
    quetype_data['name'] = "default" + str(order)
    quetype_data['question_category_type'] = que_cats[0].question_category_type.id
    quetype_data['order'] = order
    serializer = QuestionTypeSerializer(data=quetype_data)
    if serializer.is_valid():
        serializer.save()
        question['question_type_id'] = serializer.data['id']
        saved = True
    else:
        saved = False
    if(saved):    
        for que_cat in que_cats:
            print('quecat',que_cat.id)
            # Create a default+order question type
            data['question_category'] = que_cat.id
            data['question_text'] = question['question_text']
            data['label'] = question['question_text']
            data['question_type'] = question['question_type_id']
            data['team'] = team
            # here description works as a question type
            data['description'] = question['description']
            data['question_options'] = question['description']
            # data['order'] = order
            data['option1'] = question['option1']
            data['option2'] = question['option2']
            data['option3'] = question['option3']
            data['option4'] = question['option4']
            # data['team'] = team
            serializer = QuestionSaveSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                saved = True
            else:
                saved = False
        if(saved):            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# def get_question_by_team(request):
#     team = request.query_params.get('team')
#     print("team",team)
#     comp = request.query_params.get('component')
#     queryset = SdgComponents.objects.filter(id=comp, category__description="a")
#     print("queryset",queryset)
#     serializer = ComponenetSerializer(queryset, many=True)
#     return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]


# class ResultViewSet(viewsets.ModelViewSet):
#     queryset = Result.objects.all()
#     serializer_class = ResultSerializer

class ResultList(generics.ListAPIView):
    serializer_class = ResultDataSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        team = self.kwargs['team']
        return Result.objects.filter(team=team)

class ReportResultList(generics.ListAPIView):
    serializer_class = ReportResultSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        team = self.kwargs['team']
        return Result.objects.filter(team=team).order_by('question_type', 'value')


class TargetView(viewsets.ModelViewSet):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

class IndicatorView(viewsets.ModelViewSet):
    queryset = Indicator.objects.all()
    serializer_class = IndicatorSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

class SubCategoryView(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

class QuestionCategoryView(viewsets.ModelViewSet):
    queryset = QuestionCategory.objects.all()
    serializer_class = QuestionCategorySerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

class SdgComponentsView(viewsets.ModelViewSet):
    queryset = SdgComponents.objects.all()
    serializer_class = ComponenetSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

class QuestionView(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

class QuestionCategoryTypeView(viewsets.ModelViewSet):
    queryset = QuestionCategoryType.objects.all()
    serializer_class = QuestionCategoryTypeSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
