from datetime import datetime


def get_stat_count(queryset):
    today = datetime.today().date()
    all_count = queryset.count()
    month_count = queryset.filter(created_at__month__gte=today.month).count()
    day_count = queryset.filter(created_at__day__gte=today.day).count()
    # print(all_count, month_count, day_count)
    return all_count, month_count, day_count