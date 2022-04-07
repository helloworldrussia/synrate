from django.contrib import admin
from .models import Parser, ENGINE, VkGroupInfo

# Register your models here.

admin.site.register(Parser)
admin.site.register(ENGINE)
admin.site.register(VkGroupInfo)
