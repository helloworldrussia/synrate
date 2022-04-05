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
    b2b = Offer.objects.filter(home_name='b2b-center').order_by('-created_at')
    b2b_center_all, b2b_center_month, b2b_center_day = get_counts(b2b)

    etp_aktiv = Offer.objects.filter(home_name='etp-activ').order_by('-created_at')
    etp_aktiv_all, etp_aktiv_month, etp_aktiv_day = get_counts(etp_aktiv)

    etpgpb = Offer.objects.filter(home_name='etpgpb').order_by('-created_at')
    etpgpb_all, etpgpb_month, etpgpb_day = get_counts(etpgpb)

    fabrikant = Offer.objects.filter(home_name='fabrikant').order_by('-created_at')
    fabrikant_all, fabrikant_month, fabrikant_day = get_counts(fabrikant)

    isource = Offer.objects.filter(home_name='isource').order_by('-created_at')
    isource_all, isource_month, isource_day = get_counts(isource)

    nelikvidy = Offer.objects.filter(home_name='nelikvidi').order_by('created_at')
    nelikvidy_all, nelikvidy_month, nelikvidy_day = get_counts(nelikvidy)

    onlinecontract = Offer.objects.filter(home_name='onlinecontract').order_by('-created_at')
    onlinecontract_all, onlinecontract_month, onlinecontract_day = get_counts(onlinecontract)

    roseltorg = Offer.objects.filter(home_name='roseltorg').order_by('-created_at')
    roseltorg_all, roseltorg_month, roseltorg_day = get_counts(roseltorg)

    tektorg = Offer.objects.filter(home_name='tektorg').order_by('-created_at')
    tektorg_all, tektorg_month, tektorg_day = get_counts(tektorg)

    tenderpro = Offer.objects.filter(home_name='tenderpro').order_by('-created_at')
    tenderpro_all, tenderpro_month, tenderpro_day = get_counts(tenderpro)
    all = Offer.objects.all().count()

    # a = {"tenderpro": tenderpro, "tektorg": tektorg, "roseltorg": roseltorg, "onlinecontract": onlinecontract,
    #            "nelikvidy": nelikvidy, "isource": isource, "fabrikant": fabrikant, "etpgpb": etpgpb, "etp_aktiv": etp_aktiv,
    #            "b2b": b2b}
    # answer = get_time_stat(a)
    content = {"all": all,
             'tenderpro_all': tenderpro_all,
             "tenderpro_day": tenderpro_day,
             "tenderpro_month": tenderpro_month,

             "tektorg_day": tektorg_day,
             "tektorg_month": tektorg_month,
             "tektorg_all": tektorg_all,

             "roseltorg_all": roseltorg_all,
             "roseltorg_month": roseltorg_month,
             "roseltorg_day": roseltorg_day,

             "onlinecontract_all": onlinecontract_all,
             "onlinecontract_month": onlinecontract_month,
             "onlinecontract_day": onlinecontract_day,

             "nelikvidy_all": nelikvidy_all,
             "nelikvidy_month": nelikvidy_month,
             "nelikvidy_day": nelikvidy_day,

             "isource_all": isource_all,
             "isource_month": isource_month,
             "isource_day": isource_day,

             "fabrikant_all": fabrikant_all,
             "fabrikant_month": fabrikant_month,
             "fabrikant_day": fabrikant_day,

             "etpgpb_all": etpgpb_all,
             "etpgpb_month": etpgpb_month,
             "etpgpb_day": etpgpb_day,

             "etp_aktiv_all": etp_aktiv_all,
             "etp_aktiv_month": etp_aktiv_month,
             "etp_aktiv_day": etp_aktiv_day,

             "b2b_center_all": b2b_center_all,
             "b2b_center_month": b2b_center_month,
             "b2b_center_day": b2b_center_day}

    qs = ParserDetail.objects.all()
    for parser in qs:
        content[f'{parser.name}_status'] = parser.status
    return render(request, 'cabinet/cabinet_stat.html', content)

