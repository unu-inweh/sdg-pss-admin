from django.conf.urls import url, include
from rest_framework import routers
from pss_app import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'teams', views.TeamViewSet)
# router.register(r'results', views.ResultList)
router.register(r'questions', views.QuestionView) # not used
router.register(r'category', views.CategoryView) # not used
router.register(r'subcategory', views.SubCategoryView) # not used
router.register(r'questcategory', views.QuestionCategoryView) # not used
router.register(r'component', views.SdgComponentsView)
#router.register(r'auth', views.UserAuth)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^result/$', views.result),
    url(r'^result1/$', views.result1),
    url(r'^team-members/$', views.team_members),
    url(r'^results/(?P<user>.+)/$', views.ResultList.as_view()),
    url(r'^results-report/(?P<user>.+)/$', views.ReportResultList.as_view()),
    url(r'^team-summary-headings', views.team_summary_headings),
    url(r'^team-summary-results', views.team_summary_results),
    url(r'^add-question', views.add_question),
    url(r'^feedback', views.feedback),    
    url(r'^getcsrf', views.getcsrf)
    # url(r'^get-question-by-team', views.get_question_by_team)
]