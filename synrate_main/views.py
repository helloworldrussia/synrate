import operator
import time
from functools import reduce

from django.contrib.postgres.search import SearchVector, SearchRank
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.views.generic import ListView

from .mixins import get_counts, get_filter_qs, get_filters, get_random_search_queries
from .models import Offer, OfferCategory, OfferSubcategory, OffersCounter, SearchQuery
from parsers.models import Parser, ENGINE
from .forms import ParserForm, EngineForm
from rest_framework import generics
import datetime


# Create your views here.

def get_all_category_names():
    final_str = '"Все"'
    for cat in OfferCategory.objects.all():
        final_str += ","
        final_str += "'{}'".format(str(cat))
        for subcat in OfferSubcategory.objects.filter(category=cat.id):
            final_str += ","
            final_str += "'{}'".format(str(subcat))
    return final_str


def index(request):
    search_target = request.GET.get('search_target', 'additional_data')
    
    queryset = Offer.objects.all().exclude(offer_start_date__isnull=True).order_by('-offer_start_date')
    all_count, month_count, today_count = OffersCounter.get_counts('all')

    # показываем объявления, расчитав количество объяв за месяц, день и за все время,
    # передаем значения в контекст
    return render(request, 'index.html', {"offers": queryset[0:30],
                                          "all_count": all_count,
                                          "month_count": month_count,
                                          "today_count": today_count,
                                          "search_target": search_target})


def parser_admin(request):
    if request.user.is_staff:
        parsers = Parser.objects.all()
        enigines = ENGINE.objects.all()
        form = ParserForm()
        return render(request, 'parser_admin.html', {"parsers": parsers, "engines": enigines})
    else:
        return HttpResponse("Отказано в доступе")


def parser_view(request, id):
    instance = generics.get_object_or_404(Parser, id=id)
    form = ParserForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('parser_admin')
    return render(request, 'parser_detail.html', {'form': form})


def list(request, pk):
    a = "synrate.ru"
    if pk == 1:
        a = "tenderpro"
    elif pk == 2:
        a = "roseltorg"
    offers = Offer.objects.filter(home_name=a)
    return render(request, 'wasd.html', {"offers": offers})


def detail(request, pk):
    t = Offer.objects.get(id=pk)
    try:
        data = t.additional_data.split(";")
        tablestr = ""
        for d in data:
            if d != "":
                tablestr = tablestr + "<tr><td>" + d.split(":")[0] + "</td>" + "<td>" + d.split(":")[1] + "</td></tr>"
    except IndexError:
        tablestr = "<tr><td>Другие данные остутствуют<td><td><td><tr>"
    return render(request, 'detail.html', {'offer': t, "data": tablestr})


def search(request, query_slug):
    search_query = get_object_or_404(SearchQuery, slug=query_slug)
    
    url, qs = request.build_absolute_uri(), 0
    if '&page' in url or 'filter' in url:
        qs = 1

    and_dict, or_dict, word_list = get_filter_qs(request.GET)
    filtering = 0
    try:
        from_filter, search_filter, time_filter, include_text, include_region, include_org = get_filters(request.GET)
        filtering = 1
    except:
        pass
    
    search_queries = get_random_search_queries()
    queryset = Offer.objects.filter().order_by('-offer_start_date')


    year_ago_date = datetime.datetime.now() - datetime.timedelta(days=365)
    queryset = queryset.filter(offer_start_date__gte=year_ago_date)
    words = search_query.phrase.replace('.', '').replace(',', '').split(' ')

    additional_data_queryset = queryset
    words = [word  for word in words if word!='']
    for word in words:
        additional_data_queryset = additional_data_queryset.filter(additional_data__icontains=word)
    name_queryset = queryset
    for word in words:
        name_queryset = name_queryset.filter(name__icontains=word)

    queryset = name_queryset | additional_data_queryset

    all_count, month_count, today_count = OffersCounter.get_counts('all')
    
    paginator = Paginator(queryset, 30)
    if request.GET.get('page'):
        page_number = request.GET.get('page')
    else:
        page_number = 1

    page_obj = paginator.page(page_number)

    return render(request, 'filtr.html', {'offers': page_obj, "all_count": all_count,
                                        "month_count": month_count, "today_count": today_count,
                                        "qs": qs, "filtering": filtering,
                                        "from_filter": from_filter, "search_filter": search_query.phrase,
                                        "search_target":'additional_data', "from_search":True})


def search_all(request):
    return redirect("https://synrate.ru/ostatki/page=1?per_page=20")


def detail_info(request, id):
    slug = 0
    try:
        id = int(id)
    except Exception as ex:
        print(ex)
        slug = 1
    if slug:
        offer = Offer.objects.get(slug=id)
    else:
        offer = Offer.objects.get(id=id)
    offer.views += 1
    offer.save()

    year_ago_date = datetime.datetime.now() - datetime.timedelta(days=365)
    queryset = Offer.objects.filter(
        created_at__gte=year_ago_date, 
        pk__gt=offer.pk - 3, 
        pk__lte=offer.pk + 3
    ).exclude(pk=offer.pk)

    return render(request, 'newcard.html', {"offer": offer, "offers": queryset})


def category(request):
    cat = OfferSubcategory.objects.all()
    lst = []
    fin_str = ""
    prev = ""
    for c in cat:
        if c.category.name != prev:
            fin_str += "<h3>" + c.category.name + "</h3><li>" + c.name + "</li>"
            prev = c.category.name
        else:
            fin_str += "<li>" + c.name + "</li>"

    return render(request, "category.html", {"category_tags": fin_str})


def listing(request):
    url, qs = request.build_absolute_uri(), 0
    if '&page' in url or 'filter' in url:
        qs = 1

    and_dict, or_dict, word_list = get_filter_qs(request.GET)
    filtering = 0
    try:
        from_filter, search_filter, time_filter, include_text, include_region, include_org = get_filters(request.GET)
        filtering = 1
    except:
        pass
        
    queryset = Offer.objects.filter().order_by('-offer_start_date')

    search_filter = request.GET.get('search_filter', '')
    search_target = request.GET.get('search_target', 'additional_data')
    from_filter = request.GET.get('from_filter')

    if from_filter:
        queryset = queryset.filter(home_name=from_filter)

    if search_filter:
        # Сохраняем поисковый запрос пользователя
        search_query, created = SearchQuery.objects.get_or_create(phrase=search_filter)
        search_query.search_count += 1
        search_query.save()

        year_ago_date = datetime.datetime.now() - datetime.timedelta(days=365)
        queryset = queryset.filter(offer_start_date__gte=year_ago_date)
        words = search_filter.replace('.', '').replace(',', '').split(' ')

        if search_target == 'additional_data':
            additional_data_queryset = queryset
            words = [word  for word in words if word!='']
            for word in words:
                additional_data_queryset = additional_data_queryset.filter(additional_data__icontains=word)
            name_queryset = queryset
            for word in words:
                name_queryset = name_queryset.filter(name__icontains=word)

            queryset = name_queryset | additional_data_queryset

        if search_target == 'location':
            for word in words:
                queryset = queryset.filter(location__icontains=word)
        
        if search_target == 'organisation':
            for word in words:
                queryset = queryset.filter(organisation__icontains=word)


    all_count, month_count, today_count = OffersCounter.get_counts('all')
    
    paginator = Paginator(queryset, 30)
    if request.GET.get('page'):
        page_number = request.GET.get('page')
    else:
        page_number = 1

    page_obj = paginator.page(page_number)

    if filtering:
        return render(request, 'filtr.html', {'offers': page_obj, "all_count": all_count,
                                          "month_count": month_count, "today_count": today_count,
                                          "qs": qs, "filtering": filtering,
                                          "from_filter": from_filter, "search_filter": search_filter,
                                          "search_target":search_target})

    return render(request, 'filtr.html', {'offers': page_obj, "all_count": all_count,
                                          "month_count": month_count, "today_count": today_count,
                                          "qs": qs, "filtering": filtering, "search_target":search_target})

# class OffersView(ListView):
#     paginate_by = 10
#

def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)