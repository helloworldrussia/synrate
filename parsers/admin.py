from django.contrib import admin
from django.utils.html import format_html

from .models import Parser, ENGINE, VkGroupDetail, Proxy, ProxyUser, VkAccount


class VkGroupDetailAdmin(admin.ModelAdmin):

    list_display = ('name', 'vk_id', 'link',)
    search_fields = ['name', 'vk_id', 'url', ]

    def link(self, obj):
        return format_html(f"<a href='{obj.url}' target='_blank'>{obj.url}</a>", url=obj.url)


class ProxyAdmin(admin.ModelAdmin):
    list_display = ['ip', 'login', 'password', 'port']
    search_fields = ['ip', 'login', 'password', 'port']

    def render_change_form(self, request, context, *args, **kwargs):
        try:
            obj = ProxyUser.objects.get(active=True)
            form_instance = context['adminform'].form
            form_instance.fields['login'].widget.attrs['value'] = obj.login
            form_instance.fields['port'].widget.attrs['value'] = obj.port
            form_instance.fields['password'].widget.attrs['value'] = obj.password
        except:
            form_instance = context['adminform'].form
            form_instance.fields['login'].widget.attrs['value'] = ''
            form_instance.fields['password'].widget.attrs['value'] = ''
        return super().render_change_form(request, context, *args, **kwargs)


class ProxyUserAdmin(admin.ModelAdmin):
    list_display = ['login', 'password', 'port', 'active']
    search_fields = ['login', 'password', 'port', 'active']


class VkAccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'token', 'active']
    search_fields = ['name', 'token', 'active']


admin.site.register(Parser)
admin.site.register(ENGINE)
admin.site.register(VkGroupDetail, VkGroupDetailAdmin)
admin.site.register(VkAccount, VkAccountAdmin)
admin.site.register(Proxy, ProxyAdmin)
admin.site.register(ProxyUser, ProxyUserAdmin)


