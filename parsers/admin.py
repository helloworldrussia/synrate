from django.contrib import admin
from django.utils.html import format_html

from .models import Parser, ENGINE, VkGroupDetail, Proxy


class VkGroupDetailAdmin(admin.ModelAdmin):

    list_display = ('name', 'vk_id', 'link',)
    search_fields = ['name', 'vk_id', 'url', ]

    def link(self, obj):
        return format_html(f"<a href='{obj.url}' target='_blank'>{obj.url}</a>", url=obj.url)


class ProxyAdmin(admin.ModelAdmin):
    list_display = ['ip', 'login', 'password', 'port']
    search_fields = ['ip', 'login', 'password', 'port']


admin.site.register(Parser)
admin.site.register(ENGINE)
admin.site.register(VkGroupDetail, VkGroupDetailAdmin)
admin.site.register(Proxy, ProxyAdmin)

