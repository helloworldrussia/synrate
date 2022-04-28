import datetime

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from synrate_main.mixins import get_counts
from synrate_main.models import Offer, ParserDetail
from .forms import UserForm, LogInForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse


class SignUpView(CreateView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("Users:cabinet")
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
                    return redirect("Users:cabinet")
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
    today = datetime.datetime.today().date()

    b2b_center_all = Offer.objects.filter(home_name='b2b-center').count()
    b2b_center_month = Offer.objects.filter(home_name='b2b-center', created_at__month=today.month).count()
    b2b_center_day = Offer.objects.filter(home_name='b2b-center', created_at__day=today.day).count()

    etp_aktiv_all = Offer.objects.filter(home_name='etp-activ').count()
    etp_aktiv_month = Offer.objects.filter(home_name='etp-activ', created_at__month=today.month).count()
    etp_aktiv_day = Offer.objects.filter(home_name='etp-activ', created_at__day=today.day).count()


    etpgpb_all = Offer.objects.filter(home_name='etpgpb').count()
    etpgpb_month = Offer.objects.filter(home_name='etpgpb', created_at__month=today.month).count()
    etpgpb_day = Offer.objects.filter(home_name='etpgpb', created_at__day=today.day).count()

    fabrikant_all = Offer.objects.filter(home_name='fabrikant').count()
    fabrikant_month = Offer.objects.filter(home_name='fabrikant', created_at__month=today.month).count()
    fabrikant_day = Offer.objects.filter(home_name='fabrikant', created_at__day=today.day).count()


    isource_all = Offer.objects.filter(home_name='isource').count()
    isource_month = Offer.objects.filter(home_name='isource', created_at__month=today.month).count()
    isource_day = Offer.objects.filter(home_name='isource', created_at__day=today.day).count()

    nelikvidy_all = Offer.objects.filter(home_name='nelikvidi').count()
    nelikvidy_month = Offer.objects.filter(home_name='nelikvidi', created_at__month=today.month).count()
    nelikvidy_day = Offer.objects.filter(home_name='nelikvidi', created_at__day=today.day).count()

    onlinecontract_all = Offer.objects.filter(home_name='onlinecontract').count()
    onlinecontract_month = Offer.objects.filter(home_name='onlinecontract', created_at__month=today.month).count()
    onlinecontract_day = Offer.objects.filter(home_name='onlinecontract', created_at__day=today.day).count()

    roseltorg_all = Offer.objects.filter(home_name='roseltorg').count()
    roseltorg_month = Offer.objects.filter(home_name='roseltorg', created_at__month=today.month).count()
    roseltorg_day = Offer.objects.filter(home_name='roseltorg', created_at__day=today.day).count()

    tektorg_all = Offer.objects.filter(home_name='tektorg').count()
    tektorg_month = Offer.objects.filter(home_name='tektorg', created_at__month=today.month).count()
    tektorg_day = Offer.objects.filter(home_name='tektorg', created_at__day=today.day).count()

    tenderpro_all = Offer.objects.filter(home_name='tenderpro').count()
    tenderpro_month = Offer.objects.filter(home_name='tenderpro', created_at__month=today.month).count()
    tenderpro_day = Offer.objects.filter(home_name='tenderpro', created_at__day=today.day).count()

    all = Offer.objects.all().count()

    vk_all = Offer.objects.filter(home_name='vk.com').count()
    vk_month = Offer.objects.filter(home_name='vk.com', created_at__month=today.month).count()
    vk_day = Offer.objects.filter(home_name='vk.com', created_at__day=today.day).count()

    telegram_all = Offer.objects.filter(home_name='telegram').count()
    telegram_month = Offer.objects.filter(home_name='telegram', created_at__month=today.month).count()
    telegram_day = Offer.objects.filter(home_name='telegram', created_at__day=today.day).count()

    prostanki_all = Offer.objects.filter(home_name='prostanki').count()
    prostanki_month = Offer.objects.filter(home_name='prostanki', created_at__month=today.month).count()
    prostanki_day = Offer.objects.filter(home_name='prostanki', created_at__day=today.day).count()

    metaprom_all = Offer.objects.filter(home_name='metaprom').count()
    metaprom_month = Offer.objects.filter(home_name='metaprom', created_at__month=today.month).count()
    metaprom_day = Offer.objects.filter(home_name='metaprom', created_at__day=today.day).count()

    promportal_all = Offer.objects.filter(home_name='promportal').count()
    promportal_month = Offer.objects.filter(home_name='promportal', created_at__month=today.month).count()
    promportal_day = Offer.objects.filter(home_name='promportal', created_at__day=today.day).count()

    content = {"all": all,
     "vk_all": vk_all, "vk_month": vk_month, "vk_day": vk_day, 'tenderpro_all': tenderpro_all, "tenderpro_day": tenderpro_day, "tenderpro_month": tenderpro_month,
     "tektorg_day": tektorg_day, "tektorg_month": tektorg_month, "tektorg_all": tektorg_all,
     "roseltorg_all": roseltorg_all, "roseltorg_month": roseltorg_month, "roseltorg_day": roseltorg_day,
     "onlinecontract_all": onlinecontract_all, "onlinecontract_month": onlinecontract_month, "onlinecontract_day": onlinecontract_day,
     "nelikvidy_all": nelikvidy_all, "nelikvidy_month": nelikvidy_month, "nelikvidy_day": nelikvidy_day,
     "isource_all": isource_all, "isource_month": isource_month, "isource_day": isource_day,
     "fabrikant_all": fabrikant_all, "fabrikant_month": fabrikant_month, "fabrikant_day": fabrikant_day,
     "etpgpb_all": etpgpb_all, "etpgpb_month": etpgpb_month, "etpgpb_day": etpgpb_day,
     "etp_aktiv_all": etp_aktiv_all, "etp_aktiv_month": etp_aktiv_month, "etp_aktiv_day": etp_aktiv_day,
     "b2b_center_all": b2b_center_all, "b2b_center_month": b2b_center_month, "b2b_center_day": b2b_center_day,
     "telegram_all": telegram_all, "telegram_day": telegram_day, "telegram_month": telegram_month,
     "prostanki_all": prostanki_all, "prostanki_month": prostanki_month, "prostanki_day": prostanki_day,
     "metaprom_all": metaprom_all, "metaprom_month": metaprom_month, "metaprom_day": metaprom_day,
     "promportal_all": promportal_all, "promportal_month": promportal_month, "promportal_day": promportal_day
    }

    qs = ParserDetail.objects.all()
    for parser in qs:
        content[f'{parser.name}_status'] = parser.status
    return render(request, 'cabinet/cabinet_stat.html', content)

