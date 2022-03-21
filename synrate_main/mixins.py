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
    and_dict = {}
    or_dict = {}
    filtering = 0
    if data.get('time_filter'):
        if data.get('time_filter') != 'all':
            start_date = today - timedelta(days=int(data.get('time_filter')))
            start_date = start_date.date()
            and_dict['created_at__gt'] = start_date
            filtering = 1

    if data.get('from_filter'):
        and_dict['home_name'] = data.get('from_filter')
        filtering = 1

    if data.get('search_filter') is not None and data.get('search_filter') != '':
        or_dict['name__contains'] = data.get('search_filter')
        or_dict['location__contains'] = data.get('search_filter')
        or_dict['owner__contains'] = data.get('search_filter')
        or_dict['ownercontact__contains'] = data.get('search_filter')
        or_dict['additional_data__contains'] = data.get('search_filter')
        or_dict['organisation__contains'] = data.get('search_filter')
        filtering = 1

    if filtering:
        print(and_dict, or_dict)
        return and_dict, or_dict
    else:
        return 0, 0
<<<<<<< HEAD
=======


def get_filters(data):
    from_filter, search_filter, time_filter = 0, 0, 0

    filtering = 0
    if data.get('time_filter'):
        time_filter = data.get('time_filter')
        filtering = 1

    if data.get('from_filter'):
        from_filter = data.get('from_filter')
        filtering = 1

    if data.get('search_filter') is not None and data.get('search_filter') != '':
        search_filter = data.get('search_filter')
        filtering = 1

    if filtering:
        return from_filter, search_filter, time_filter
    else:
        return 0
>>>>>>> b25b5637e835ae6022ed1c90b5775720bdd810e4
