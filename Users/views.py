from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from .forms import UserForm, LogInForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse


# Sign Up View
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




