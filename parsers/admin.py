from django.contrib import admin
from .models import Parser, ENGINE, VkGroupDetail


class VkGroupDetailAdmin(admin.ModelAdmin):
    list_display = ('name', 'vk_id', 'url',)
    search_fields = ['name', 'vk_id', 'url', ]

admin.site.register(Parser)
admin.site.register(ENGINE)
admin.site.register(VkGroupDetail, VkGroupDetailAdmin)
