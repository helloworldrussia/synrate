from django.urls import path, include
from . import views
from .models import Parser, ENGINE
from django.conf.urls import url
urlpatterns = [
    path('offers/list', views.OfferListView.as_view(), name='offer-list'),
    path('offers/create', views.OfferCreateView.as_view(), name='offer-create'),
    path('parser/list', views.ParserListView.as_view(), name='parser-list'),
    path('parser/update/<int:pk>/', views.ParserUpdateView.as_view(), name='parser-update'),
    path('ENGINE/list', views.EngineListView.as_view(), name='engine-list'),
    path('ENGINE/update/<int:pk>/', views.EngineUpdateView.as_view(), name='engine-update')
]