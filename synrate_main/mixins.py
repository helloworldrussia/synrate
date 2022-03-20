from datetime import datetime, timedelta
from synrate_main.models import Offer


# принимаем кверисет, возвращает три переменные с количеством созданных объяв за все время, текущ. мес., день
def get_counts(queryset):
    today = datetime.today().date()
    all_count = queryset.count()
    month_count = queryset.filter(created_at__month__gte=today.month).count()
    day_count = queryset.filter(created_at__day__gte=today.day).count()
    # print(all_count, month_count, day_count)
    return all_count, month_count, day_count


# функция для распаковки request.POST из filter/
def get_filter_qs(data):
    print(data)
    today = datetime.today()
    filter_dict = {}
    filtering = 0
    if data.get('time_filter'):
        start_date = today - timedelta(days=int(data.get('time_filter')))
        start_date = start_date.date()
        filter_dict['created_at__gt'] = start_date
        filtering = 1

    if data.get('from_filter'):
        filter_dict['home_name'] = data.get('from_filter')
        filtering = 1

    if filtering:
        return filter_dict
    else:
        return 0
