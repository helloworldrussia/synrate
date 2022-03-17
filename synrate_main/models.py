import datetime

from django.db import models
from cms.models import CMSPlugin


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


class Offer(models.Model):
    name = models.CharField(max_length=300, null=True, blank=True, default=None, unique=True, verbose_name="Название")
    home_name = models.CharField(max_length=200, null=True, blank=True, default=None, verbose_name="Источник")
    url = models.CharField(max_length=250, unique=True, null=True, blank=True, default=None,
                           verbose_name="Ссылка на источник")
    location = models.CharField(max_length=250, null=True, blank=True, default="РФ", verbose_name="Регион")
    offer_type = models.CharField(max_length=100, null=True, blank=True, default="Продажа",
                                  verbose_name="Тип объявления")
    offer_start_date = models.DateField(null=True, blank=True, verbose_name="Дата начала торгов")
    offer_end_date = models.DateField(null=True, blank=True, verbose_name="Дата завершения торгов")
    owner = models.CharField(max_length=100, null=True, blank=True, default=None, verbose_name="Владелец")
    ownercontact = models.CharField(max_length=250, null=True, blank=True, default="Не указан",
                                    verbose_name="Контакт владельцы")
    offer_price = models.IntegerField(null=True, blank=True, default=None, verbose_name="Цена")
    additional_data = models.TextField(null=True, blank=True, default=None, verbose_name="Дополнительные данные")
    organisation = models.CharField(max_length=250, null=True, blank=True, default=None, verbose_name="Организация")
    views = models.IntegerField(default=0, blank=True, verbose_name="Просмотры")
    category = models.ForeignKey(OfferSubcategory, on_delete=models.CASCADE, verbose_name="Подкатегория",
                                 null=True, default=None, blank=True, related_name="subcategory")
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"


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
