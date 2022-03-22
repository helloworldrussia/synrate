from django.contrib import admin
from .models import Offer, FAQ, OfferCategory, OfferSubcategory


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    pass


@admin.register(OfferCategory)
class OfferCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(OfferSubcategory)
class OfferSubcategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    pass
