from django.contrib import admin
from .models import SynrateUser


class SynrateUserAdmin(admin.ModelAdmin):
    verbose_name_plural = 'userprofiles'
    can_delete = False


# Register your models here.


admin.site.register(SynrateUser, SynrateUserAdmin)
