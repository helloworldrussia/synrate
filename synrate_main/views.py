from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import Offer, OfferCategory, OfferSubcategory
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
    most_viewed = Offer.objects.all().order_by('offer_end_date')
    return render(request, 'index.html', {"offers": most_viewed[0:10]})


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


def search(request, args: str = ''):
    page = 1
    if request.META["QUERY_STRING"] != "" and request.META["QUERY_STRING"] is not None:
        args += "?" + request.META["QUERY_STRING"]
    else:
        args += "?key=DMT"
    s = args.split("?")
    t = Offer.objects.all()
    page_found = False
    per_page = 20

    for a in s:
        try:
            frst = a.split("=")[0]
            sec = a.split("=")[1]
        except IndexError:
            pass
        if frst == "per_page":
            if int(sec) <= 100:
                per_page = int(sec)
            else:
                per_page = 20
        if frst == "page":
            if not page_found:
                page = int(sec)
                page_found = True
            else:
                return redirect("https://synrate.ru/ostatki/{}".format(("page={}".format(sec)) + "?" +
                                str(request.META["QUERY_STRING"]).replace("page={}".format(page), "")
                                                                       .replace("?page={}".format(sec), "")))
        if frst == "time_mt":
            k = []
            if sec == "day":
                timez = datetime.date.today() - datetime.timedelta(days=1)
            elif sec == "week":
                timez = datetime.date.today() - datetime.timedelta(days=7)
            elif sec == "month":
                timez = datetime.date.today() - datetime.timedelta(days=30)
            else:
                timez = datetime.date(int(sec.split(",")[0]), int(sec.split(",")[1]), int(sec.split(",")[2]))
            for obj in t:
                if obj.offer_start_date is not None:
                    if obj.offer_start_date >= timez:
                        k.append(obj)
            t = k
        if frst == "time_lt":
            k = []
            timez = datetime.date(int(sec.split(",")[0]), int(sec.split(",")[1]), int(sec.split(",")[2]))
            for obj in t:
                if obj.offer_start_date >= timez:
                    k.append(obj)
            t = k
        if frst == "source":
            k = []
            for obj in t:
                if obj.home_name == sec:
                    k.append(obj)
            t = k
        if frst == "location":
            k = []
            for obj in t:
                if obj.location == sec:
                    k.append(obj)
            t = k
        if frst == "keywords":
            sec = sec.replace(u" ", ",")
            if len(sec.split(",")) > 20:
                return HttpResponse("Нельхя вводить больше 20 ключевых слов")

            for keyword in sec.split(","):
                k = []
                for obj in t:
                    if obj.name.lower().find(keyword.lower()) != -1:
                        k.append(obj)
                t = k
        if frst == "category":
            if frst.find("/") != -1:
                cat = frst.split("/")[0]
                subcat = frst.split("/")[1]
                k = []
                for obj in t:
                    if frst.category.name.replace(" ", "").replace("%20", "").strip() == subcat.strip():
                        k.append(obj)
                t = k

    if len(t) == 0:
        return HttpResponse("Ничего с параметрами {} найдено".format(args))

    paginator = Paginator(t, per_page)
    offers = paginator.page(page)
    category_list_str = get_all_category_names()

    return render(request, 'filtr.html', {"offers": offers, "category_list": category_list_str,
                                          "query": request.META["QUERY_STRING"]})


def search_all(request):
    return redirect("https://synrate.ru/ostatki/page=1?per_page=20")


def detail_info(request, id):
    t = Offer.objects.get(id=id)
    t.views += 1
    t.save()
    t = Offer.objects.get(id=id)
    return render(request, 'card.html', {"offer": t})


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
