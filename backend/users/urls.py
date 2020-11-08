from django.urls import path
from users import views

app_name = 'users'
urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('email-verify/', views.EmailVerifyView.as_view(), name='email-verify'),
]