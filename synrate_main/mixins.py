import random
from datetime import datetime, timedelta
from django.db.models import Max, Min

from synrate_main.models import Offer, SearchQuery


# принимаем кверисет, возвращает три переменные с количеством созданных объяв за все время, текущ. мес., день
def get_counts(queryset):
    today = datetime.today().date()
    all_count = queryset.count()
    month_count = queryset.filter(created_at__month=today.month).count()
    day_count = queryset.filter(created_at__day=today.day).count()
    # print(all_count, month_count, day_count)
    return all_count, month_count, day_count


# функция для распаковки request.POST из filter/
def get_filter_qs(data):
    today = datetime.today()
    and_dict = {}
    or_dict = {}
    word_list = []
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

        if data.get('include_org') is not None and data.get('include_org') != '':
            or_dict['organisation__icontains'] = data.get('search_filter')

        if data.get('include_region') is not None and data.get('include_region') != '':
            or_dict['location__icontains'] = data.get('search_filter')

        if (data.get('include_text') is not None and data.get('include_text') != '') or (data.get('include_org') is None and data.get('include_region') is None):
            or_dict['additional_data__icontains'] = data.get('search_filter')

        #or_dict['name__icontains'] = data.get('search_filter')
        #or_dict['owner__icontains'] = data.get('search_filter')
        #or_dict['ownercontact__icontains'] = data.get('search_filter')
        word_list = []
        word_list.append(data.get('search_filter'))
        word_list = word_list+data.get('search_filter').replace('.', '').replace(',', '').split(' ')
        filtering = 1

    if filtering:
        return and_dict, or_dict, word_list
    else:
        return 0, 0, 0


def get_filters(data):
    from_filter, search_filter, time_filter, include_text, include_region, include_org = 0, 0, 0, 0, 0, 0

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

    if data.get('include_text') is not None and data.get('include_text') != '':
        include_text = data.get('include_text')
        filtering = 1

    if data.get('include_region') is not None and data.get('include_region') != '':
        include_region = data.get('include_region')
        filtering = 1

    if data.get('include_org') is not None and data.get('include_org') != '':
        include_org = data.get('include_org')
        filtering = 1

    if not include_org and not include_region:
        include_text = 'on'
        filtering = 1

    if filtering:
        return from_filter, search_filter, time_filter, include_text, include_region, include_org
    else:
        return 0


def get_random_search_queries():
    try:
        # max_id = SearchQuery.objects.all().aggregate(max_id=Max("id"))['max_id']
        # min_id = SearchQuery.objects.all().aggregate(min_id=Min("id"))['min_id']
        # ids_sample = random.sample(range(min_id, max_id), 10)
        # search_queries = SearchQuery.objects.filter(id__in=ids_sample)

        search_queries_ids = SearchQuery.objects.filter(offers_count__gte=3).values_list("id", flat=True)
        random_ids = random.sample(set(search_queries_ids), 10)
        search_queries = SearchQuery.objects.filter(pk__in=random_ids)
        return search_queries
    except:
        return []
