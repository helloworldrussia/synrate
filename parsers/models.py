from django.db import models

# Create your models here.


class Parser(models.Model):
    name = models.CharField(max_length=300, unique=True, verbose_name="Название")
    text = models.TextField(null=True, blank=True, verbose_name="Описание")
    source = models.CharField(max_length=150, null=True, blank=True, verbose_name="Источник")
    unique_code = models.CharField(max_length=150, unique=True, verbose_name="Идентификатор")
    status = models.BooleanField(default=False, blank=True, verbose_name="Статус")
    time_started = models.DateTimeField(null=True, blank=True, verbose_name="Время последнего запуска")
    time_finished = models.DateTimeField(null=True, blank=True, verbose_name="Время остановки")
    offers_parsed = models.IntegerField(blank=True, null=True, default=None,
                                        verbose_name="Спаршено объявлений")
    message = models.TextField(blank=True, null=True, verbose_name="Сообщение")
    error = models.TextField(blank=True, null=True, verbose_name="Все ошибки")
    current_error = models.TextField(blank=True, null=True, verbose_name="Актуальные ошибки")
    timer = models.IntegerField(default=3600, null=True, blank=True, verbose_name="Задержка между прогонами (сек)")
    parsed = models.IntegerField(default=0, null=False, blank=False, verbose_name="Спаршено объявлений")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Парсер"
        verbose_name_plural = "Парсеры"


class ENGINE(models.Model):
    name = models.CharField(max_length=250, unique=True, verbose_name="Название")
    text = models.TextField(null=True, blank=True, verbose_name="Описание")
    unique_code = models.CharField(max_length=150, unique=True, verbose_name="Идентификатор")
    parsed = models.IntegerField(null=True, blank=True, verbose_name="Спаршено объявлений")
    status = models.BooleanField(default=False, blank=True, verbose_name="Статус")
    message = models.TextField(blank=True, null=True, verbose_name="Сообщение")
    error = models.TextField(blank=True, null=True, verbose_name="Код ошибки")
    current_log = models.TextField(blank=True, null=True, verbose_name="Актуальный лог")
    full_log = models.TextField(blank=True, null=True, verbose_name="Полный лог")
    timer = models.IntegerField(default=5, null=True, blank=True, verbose_name="Задержка прослушки (сек)")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Движок"
        verbose_name_plural = "Движки"


class Info(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Парсер")
    start_page = models.IntegerField(null=True, default=1, blank=True)


class VkGroupDetail(models.Model):
    url = models.CharField(max_length=599, unique=True, verbose_name="Ссылка группу")
    vk_id = models.IntegerField(unique=True, verbose_name='id группы ВК. С минусом. "-11111111"')
    name = models.CharField(max_length=255, unique=True, verbose_name='Название группы')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Группа ВК"
        verbose_name_plural = "Группы ВК"
