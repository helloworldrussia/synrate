from django.contrib import admin
from django.utils.html import format_html

from .models import Parser, ENGINE, VkGroupDetail


class VkGroupDetailAdmin(admin.ModelAdmin):

    list_display = ('name', 'vk_id', 'show_url',)
    search_fields = ['name', 'vk_id', 'url', ]

    def show_url(self, obj):
        return format_html(f"<a href='{obj.url}' target='_blank'>{obj.url}</a>", url=obj.url)


admin.site.register(Parser)
admin.site.register(ENGINE)
admin.site.register(VkGroupDetail, VkGroupDetailAdmin)
