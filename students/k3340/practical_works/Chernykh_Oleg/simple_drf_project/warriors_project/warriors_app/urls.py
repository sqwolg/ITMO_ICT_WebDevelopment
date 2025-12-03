from django.urls import path
from .views import *


app_name = "warriors_app"


urlpatterns = [
   path('warriors/', WarriorAPIView.as_view()),
   path('profession/create/', ProfessionCreateView.as_view()),
   path('skills/', SkillAPIView.as_view()),
   path('warriors/list/', WarriorListAPIView.as_view()),
   path('profession/generic_create/', ProfessionCreateAPIView.as_view()),
   path('warriors/with_profession/', WarriorWithProfessionAPIView.as_view()),
   path('warriors/with_skills/', WarriorWithSkillsAPIView.as_view()),
   path('warriors/<int:pk>/', WarriorDetailAPIView.as_view()),
]