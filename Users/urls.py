from django.urls import path
from .views import SignUpView, user_login, user_cabinet, user_logout
from . import views
app_name = 'Users'
urlpatterns = [
    path('register', SignUpView.as_view(), name='register'),
    path('login', user_login, name='login'),
    path('cabinet', user_cabinet, name='cabinet'),
    path('logout', user_logout, name='logout')
]