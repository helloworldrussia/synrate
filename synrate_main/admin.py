from django.contrib import admin

from .models import Offer, FAQ, OfferCategory, OfferSubcategory


# @admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):

    list_display = ['short_name', 'organisation', 'offer_start_date', 'home',]
    search_fields = ['name', 'organisation', 'offer_start_date', 'home_name',
                     'home_name', 'url', 'location', 'offer_type',
                     'offer_end_date', 'owner',
                     'ownercontact', 'offer_price', 'additional_data',
                     'category', 'created_at', 'from_id', 'short_cat', 'owner_id',]

    def short_name(self, obj):
        return obj.name[:25]

    def home(self, obj):
        home, nice_home_name = obj.home_name, obj.home_name

        if home == "nelikvidi":
            nice_home_name = 'nelikvidi.com'
        if home == "onlinecontract":
            nice_home_name = 'onlinecontract.ru'
        if home == "tektorg":
            nice_home_name = 'tektorg.ru'
        if home == "tenderpro":
            nice_home_name = 'tender.pro'
        if home == "isource":
            nice_home_name = 'reserve.isource.ru'
        if home == "etpgpb":
            nice_home_name = 'etpgpb.ru'
        if home == "fabrikant":
            nice_home_name = 'fabrikant.ru'
        if home == "etp-activ":
            nice_home_name = 'etp-activ.ru'
        if home == "b2b-center":
            nice_home_name = 'b2b-center.ru'
        if home == "vk.com":
            nice_home_name = 'vk.com'

        return nice_home_name

# @admin.register(OfferCategory)
class OfferCategoryAdmin(admin.ModelAdmin):
    pass
#
#
# @admin.register(OfferSubcategory)
class OfferSubcategoryAdmin(admin.ModelAdmin):
    pass
#
#
# @admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    pass

admin.site.register(OfferSubcategory, OfferSubcategoryAdmin)
admin.site.register(OfferCategory, OfferCategoryAdmin)
admin.site.register(FAQ, FAQAdmin)

admin.site.register(Offer, OfferAdmin)
