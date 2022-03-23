from django.urls import path
from .views import SignUpView, user_login, user_cabinet, user_logout, \
    CabinetView, CabinetPaymentView, CabinetFavView
from . import views
app_name = 'Users'


urlpatterns = [
    path('register', SignUpView.as_view(), name='register'),
    path('login', user_login, name='login'),
    path('cabinet', user_cabinet, name='cabinet'),
    path('logout', user_logout, name='logout'),
    path('lk', CabinetView.as_view(), name='cabinet_lk'),
    path('payment', CabinetPaymentView.as_view(), name='cabinet_payment'),
    path('fav', CabinetFavView.as_view(), name='cabinet_fav'),

]