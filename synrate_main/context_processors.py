from django.shortcuts import get_object_or_404
from .mixins import get_random_search_queries

from .models import Banner

def banners(request):
    banners = Banner.objects.filter(is_active=True)

    return {
        "right_banners": banners.filter(banner_type="right"), 
        "top_banners": banners.filter(banner_type="top"), 
        "bottom_banners": banners.filter(banner_type="bottom"), 
        "search_queries": get_random_search_queries()
    }
