from django.urls import path, re_path
from . import views
app_name = 'synrate_main'
urlpatterns = [
    path('', views.index, name="index"),
    path('parser_admin/', views.parser_admin, name='parser_admin'),
    path('offer_list/<int:pk>', views.list, name="list"),
    path('offer_detail/<int:pk>', views.detail, name="detail"),
    path('ostatki/<str:args>', views.search, name="search"),
    path('ostatki', views.search_all, name="search_all"),
    path('categories', views.category, name="category_list"),
    path('detail/<int:id>', views.detail_info, name="detail_view"),
]