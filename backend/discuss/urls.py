# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#     Copyright 2020 QandA-vietnam.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from django.urls import path
from discuss import views


app_name = "discuss"
urlpatterns = [
    path('questions/', views.QuestionListView.as_view(), name='list_questions'),
    path('questions/create/', views.QuestionCreationView.as_view(), name='create'),
    path('questions/<int:id>/', views.QuestionDetailView.as_view(), name='detail'),
    path('questions/edit/<int:id>/', views.QuestionContentView.as_view(), name='edit-question-content'),
    path('questions/<int:id>/update-delete/', views.QuestionUpdateDestroyView.as_view(), name='update'),
    path('questions/<int:id>/answers/', views.AnswerListInQuestionView.as_view(), name='answers-belong-to-question'),
    path('questions/<int:id>/best-answer/', views.AnswerAcceptedView.as_view()),
    path('answers/create/', views.AnswerCreationView.as_view(), name='answer-creation'),
    path('answers/<int:id>/update-delete/', views.AnswerUpdateDestroyView.as_view(), name='answer-update'),
    path('answers/edit/<int:id>/', views.AnswerContentView.as_view(), name='edit-answer-content'),
    path('post/<int:id>/comment/', views.CommentCreationView.as_view()),
    path('post/<int:id>/comment/all/', views.CommentListView.as_view()),
    path('<str:type>/<int:id>/<str:action>/', views.VoteView.as_view(), name='vote'),
    path('search/', views.SearchView.as_view(), name='search-post')
]
