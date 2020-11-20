from django.urls import path
from discuss import views


app_name = "discuss"
urlpatterns = [
    path('', views.QuestionListView.as_view(), name='list_questions'),
    path('create/', views.QuestionCreationView.as_view(), name='create'),
    path('<int:id>/', views.QuestionDetailView.as_view(), name='detail'),
    path('<int:id>/answer', views.AnswerCreationView.as_view(), name='answer-creation'),
]
