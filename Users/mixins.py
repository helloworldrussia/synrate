from datetime import datetime
from django.utils.timezone import localtime, now


def get_stat_count(queryset):
    today = datetime.today().date()
    all_count = queryset.count()
    month_count = queryset.filter(created_at__month__gte=today.month).count()
    day_count = queryset.filter(created_at__day__gte=today.day).count()
    # print(all_count, month_count, day_count)
    return all_count, month_count, day_count


def get_time_stat(data):
    # request = {"tenderpro": tenderpro, "tektorg": tektorg, "roseltorg": roseltorg, "onlinecontract": onlinecontract,
    #            "nelikvidy": nelikvidy, "isource": isource, "fabrikant": fabrikant, "etpgpb": etpgpb,
    #            "etp_aktiv": etp_aktiv,
    #            "b2b": b2b}
    # now = datetime.datetime.now()

    answer = {}
    try:
        nelikvidy = data["nelikvidy"][0]
        print(nelikvidy)
        time = nelikvidy.created_at
        result = localtime(now()) - time
        print(localtime(now()), time)
        print(result)
    except Exception as ex:
        print(ex)
    return 0