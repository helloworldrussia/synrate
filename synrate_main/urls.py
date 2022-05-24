from django.conf.urls import url
from django.urls import path, re_path
from . import views


app_name = 'synrate_main'
urlpatterns = [
    path('', views.index, name="index"),
    path('parser_admin/', views.parser_admin, name='parser_admin'),
    path('offer_list/<int:pk>', views.list, name="list"),
    # path('offer_detail/<int:pk>', views.detail, name="detail"),
    path('offer/ostatki/<str:query_slug>/', views.search, name="search"),
    path('ostatki', views.search_all, name="search_all"),
    path('categories', views.category, name="category_list"),
    path('offer/id/<str:id>', views.detail_info, name="detail_view"),
    # re_path(r'^filter/$', views.listing, name="filtration"),

    re_path(r'^offers/$', views.listing, name="filtration"),
]

