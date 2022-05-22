from django.db import models
from cms.models import CMSPlugin
from datetime import datetime, timedelta
from django.contrib.postgres.indexes import GinIndex, OpClass, Index
from django.db.models.functions import Upper

class OfferCategory(models.Model):
    name = models.CharField(max_length=1000, null=False, unique=True, verbose_name="Название")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class OfferSubcategory(models.Model):
    name = models.CharField(max_length=1000, null=False, unique=False, verbose_name="Название")
    category = models.ForeignKey(OfferCategory, on_delete=models.CASCADE, verbose_name="Категория", null=True,
                                 default=None, related_name="category")

    def __str__(self):
        return self.category.name + " / " + self.name

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"


class ParserDetail(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, default=None)
    status = models.TextField(null=True, blank=True, default=None)
    last_process_page = models.IntegerField(null=True, blank=True, default=1)


class Offer(models.Model):
    name = models.CharField(max_length=1500, null=True, blank=True, default=None, verbose_name="Название")
    home_name = models.CharField(max_length=200, null=True, blank=True, default=None, verbose_name="Источник")
    slug = models.CharField(max_length=255, unique=True, blank=True, null=True, default=None, verbose_name='ЧПУ')
    url = models.CharField(max_length=599, null=True, blank=True, default=None,
                           verbose_name="Ссылка на источник")
    location = models.CharField(max_length=250, null=True, blank=True, default="РФ", verbose_name="Регион")
    offer_type = models.CharField(max_length=100, null=True, blank=True, default="Продажа",
                                  verbose_name="Тип объявления")
    offer_start_date = models.DateField(null=True, blank=True, verbose_name="Дата начала торгов")
    offer_end_date = models.DateField(null=True, blank=True, verbose_name="Дата завершения торгов")
    owner = models.CharField(max_length=100, null=True, blank=True, default=None, verbose_name="Владелец")
    ownercontact = models.CharField(max_length=250, null=True, blank=True, default="Не указан",
                                    verbose_name="Контакт владельцы")
    offer_price = models.FloatField(null=True, blank=True, default=None, verbose_name="Цена")
    additional_data = models.TextField(null=True, blank=True, default=None, verbose_name="Дополнительные данные", db_index=True)
    organisation = models.CharField(max_length=250, null=True, blank=True, default=None, verbose_name="Организация")
    views = models.IntegerField(default=0, blank=True, verbose_name="Просмотры")
    category = models.ForeignKey(OfferSubcategory, on_delete=models.CASCADE, verbose_name="Подкатегория",
                                 null=True, default=None, blank=True, related_name="subcategory")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    from_id = models.TextField(blank=True, null=True, default='', verbose_name='ID от источника')
    short_cat = models.TextField(blank=True, null=True, default=None)
    owner_id = models.IntegerField(blank=True, null=True, default=None, db_index=True)
    # True - заявка опубликована, False - не опубликована и показывать ее не нужно.
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"


class OffersCounter(models.Model):
    """ Модель для хранения количества офферов для разных источников """
    HOME_CHOICES = (
        ("all", "Все"),
        ("b2b-center", "b2b-center.ru"),
        ("etp-activ", "etp-activ.ru"),
        ("etpgpb", "etpgpb.ru"),
        ("fabrikant", "fabrikant.ru"),
        ("isource", "reserve.isource.ru"),
        ("nelikvidi", "nelikvidi.com"),
        ("onlinecontract", "onlinecontract.ru"),
        ("roseltorg", "roseltorg.ru"),
        ("tektorg", "tektorg.ru"),
        ("tenderpro", "tender.pro"),
        ("vk.com", "vk.com"),
        ("telegram", "telegram"),
        ("prostanki", "prostanki.com"),
        ("metaprom", "metaprom.ru"),
        ("promportal", "promportal.su"),
    )
    # source = models.ForeignKey(ParserDetail)
    home_lilter = models.CharField(choices=HOME_CHOICES, default="all", max_length=50, verbose_name="Фильтр по источнику предложений")
    all_count = models.PositiveIntegerField(default=0)
    month_count = models.PositiveIntegerField(default=0)
    today_count = models.PositiveIntegerField(default=0)

    @staticmethod
    def reaculculate_all_counts():
        for home_filter_slug, home_filter_name in OffersCounter.home_lilter.field.choices:
            counter, created = OffersCounter.objects.get_or_create(home_lilter=home_filter_slug)
            counter.recalculate_count()

    @staticmethod
    def get_counts(filter):
        counter, created = OffersCounter.objects.get_or_create(home_lilter=filter)
        return counter.all_count, counter.month_count, counter.today_count
    
    # def recalculate_by_filter(filter):
    #     counter, created = OffersCounter.objects.get_or_create(home_lilter=filter)
    #     counter.recalculate_count()

    def recalculate_count(self):
        if self.home_lilter == "all":
            offers = Offer.objects.filter().order_by('created_at')   
        else: 
            offers = Offer.objects.filter(home_name=self.home_lilter).order_by('created_at')
        today = datetime.today().date()
        self.all_count = offers.count()
        self.month_count = offers.filter(created_at__month=today.month).count()
        self.today_count = offers.filter(created_at__day=today.day).count()
        self.save()
    

class FAQ(CMSPlugin):
    title = models.CharField(max_length=1000, null=False, default=None, verbose_name="FAQ title")
    text = models.TextField(null=False, verbose_name="FAQ text")

    def get_title(self):
        return self.title

    def __str__(self):
        return self.get_title()


class INTRO(CMSPlugin):
    header_text = models.TextField(null=False, verbose_name="Текст заголовка")
    first_title = models.CharField(max_length=1000, null=False, default=None, verbose_name="Первый заголовок")
    first_text = models.CharField(max_length=1000, null=False, default=None, verbose_name="Первый текст")
    second_title = models.CharField(max_length=1000, null=False, default=None, verbose_name="Второй заголовок")
    second_text = models.CharField(max_length=1000, null=False, default=None, verbose_name="Второй текст")
    goto_text = models.CharField(max_length=1000, null=False, default=None, verbose_name="Текст ссылки на поиск")

    def get_title(self):
        return self.header_text

    def __str__(self):
        return self.get_title()


class ABOUT(CMSPlugin):
    title = models.TextField(null=False, verbose_name="Заголовок")
    text = models.TextField(null=False, verbose_name="Текст")

    def get_title(self):
        return self.title

    def __str__(self):
        return self.get_title()


class TITLE(CMSPlugin):
    name = models.TextField(null=False, verbose_name="Заголовок")

    def get_title(self):
        return self.name

    def __str__(self):
        return self.get_title()


class CONTACT(CMSPlugin):
    name = models.TextField(null=False, verbose_name="Имя автора")
    img = models.ImageField(null=True, verbose_name="Фото автора")
    text = models.TextField(null=True, verbose_name="Описание контакта")
    contact_vk = models.CharField(null=True, max_length=2000, verbose_name="Контакт автора (ссылка вк)", blank=True)
    contact_tg = models.CharField(null=True, max_length=2000, verbose_name="Контакт автора (ссылка тг)", blank=True)
    contact_phone = models.CharField(null=True, max_length=2000, verbose_name="Контакт автора (номер телефона)",
                                     blank=True)
    contact_email = models.CharField(null=True, max_length=2000, verbose_name="Контакт автора (почта)", blank=True)

    def get_title(self):
        return self.name

    def __str__(self):
        return self.get_title()


class VkUser(models.Model):
    from_id = models.IntegerField(unique=True, null=False)
    a_data = models.TextField(null=True)


class TgUser(models.Model):
    from_id = models.IntegerField(unique=True, null=False)
    a_data = models.TextField(null=True)
