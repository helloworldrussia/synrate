from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', include('synrate_main.urls')),
    path('api/', include('parsers.urls')),
    path('api-auth', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path('info/', include('cms.urls')),
    path('user/', include('Users.urls', namespace='Users')),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "synrate_main.views.page_not_found_view"

if settings.LOCAL_SETTINGS_EXISTS and settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)),] + urlpatterns
