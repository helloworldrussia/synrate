import datetime

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from synrate_main.mixins import get_counts
from synrate_main.models import Offer, ParserDetail, OffersCounter
from .forms import UserForm, LogInForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse


class SignUpView(CreateView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("Users:cabinet_lk")
        self.object = None
        return super().get(request, *args, **kwargs)
    form_class = UserForm
    success_url = reverse_lazy('Users:login')
    template_name = 'registr.html'


def user_login(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("Users:cabinet_lk")
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        if not (request.user.is_authenticated):
            form = LogInForm()
        else:
            return redirect('Users:cabinet')

    return render(request, 'enter.html', {'form': form})


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect("synrate_main:index")
    else:
        return redirect("Users:login")


def user_cabinet(request):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return redirect('Users:login', permanent=True)
        else:
            return render(request, "user_base.html")


class CabinetView(TemplateView):
    template_name = 'cabinet/cabinet_settings.html'


class CabinetPaymentView(TemplateView):
    template_name = 'cabinet/cabinet_payment.html'


class CabinetFavView(TemplateView):
    template_name = 'cabinet/cabinet_fav.html'


class CabinetTariffView(TemplateView):
    template_name = 'cabinet/cabinet_tariff.html'


def stat_view(request):
    context = { "offer_sources": []}
    translation_dict = {
        "all": "all",
        "b2b-center": "b2b_center",
        "etp-activ": "etp_aktiv",
        "etpgpb": "etpgpb",
        "fabrikant": "fabrikant",
        "isource": "isource",
        "nelikvidi": "nelikvidy",
        "onlinecontract": "onlinecontract",
        "roseltorg": "roseltorg",
        "tektorg": "tektorg",
        "tenderpro": "tenderpro",
        "vk.com": "vk",
        "telegram": "telegram",
        "prostanki": "prostanki",
        "metaprom": "metaprom",
        "promportal": "promportal",
    }

    for source_slug, source_name in OffersCounter.home_lilter.field.choices:
        try:
            status = ParserDetail.objects.get(name=translation_dict.get(source_slug)).status
        except ParserDetail.DoesNotExist:
            status = "Не известен"
        
        all_count, month_count, day_count = OffersCounter.get_counts(source_slug)
        context["offer_sources"].append({
            "name": source_name, 
            "all_count": all_count,
            "month_count": month_count,
            "day_count": day_count,
            "status": status
        })
    return render(request, 'cabinet/cabinet_stat.html', context)
