import self as self
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import transaction, IntegrityError
from django.http import HttpResponseRedirect, Http404, HttpResponseServerError
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import views, logout
from django.contrib.auth.views import LogoutView, logout_then_login
from django.views.generic import RedirectView
from django.views.generic.list import ListView
from .models import UserInfos, TradeToRomeCode, RomeCode, Company
from .forms import RegistrationForm, ChangeAddressForm
from django.contrib.auth.decorators import login_required
import requests
import json
from decouple import config


def logoutAndLogin(request):
    """
    Logout the user and redirect to login page
    """
    return logout_then_login(request, login_url=reverse('login'))


@require_http_methods(["GET"])
@login_required
def index(request):
    """
    Index page
    """
    return redirect('main_platform:account')


@require_http_methods(["GET"])
def registrationPage(request):
    """
    Display registration page
    """
    if request.user.is_authenticated:
        return redirect('main_platform:index')

    form = RegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'main_platform/registration.html', context)


@require_http_methods(["POST"])
def registration(request):
    """
    Register new user
    """
    context = {}
    form = RegistrationForm(request.POST)
    if form.is_valid():
        password = form.cleaned_data['password']
        email = form.cleaned_data['email']
        username = form.cleaned_data['username']
        try:
            with transaction.atomic():
                user = User.objects.create_user(username, email, password)
                user = authenticate(request, username=username,
                                    password=password)
                login(request, user)
                UserInfos.objects.create(user=user)
                return redirect('main_platform:account')
        except FileNotFoundError:
            form.errors['internal'] = ("Erreur interne, "
                                       "merci de réitérer votre requête")

            return redirect('main_platform:registrationPage')
    else:
        context = {'form': form, 'errors': form.errors.items()}
        return render(request, 'main_platform/registration.html',
                      context)


@login_required
def saveCompany(request):
    """
    Save a company for a user
    """
    with transaction.atomic():
        try:
            user = request.user
            siret = request.POST.get('siret')
            if Company.objects.filter(siret=siret).count() < 1:
                name = request.POST.get('name')
                headcount_text = request.POST.get('headcount_text')
                contact_mode = request.POST.get('contact_mode')
                url = request.POST.get('url')
                alternance = request.POST.get('alternance')
                Company.objects.create(name=name,
                                       headcount_text=headcount_text,
                                       contact_mode=contact_mode,
                                       url=url,
                                       alternance=alternance,
                                       siret=siret)

            Company.objects.filter(siret=siret)[0].users.add(user)
        except Exception as e:
            print(e)

    return HttpResponseRedirect(request.path_info)


@login_required
def searchCompany(request):
    """
    Job search page
    """
    user_info = UserInfos.objects.filter(user=request.user)[0]
    CLIENTID = config('CLIENTID')
    CLIENTSECRET = config('CLIENTSECRET')
    if user_info is not None and user_info.address is not None:
        token = requests.post("https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=%2Fpartenaire",
                              data={"grant_type": "client_credentials", "realm": "/partenaire",
                                    "content-type": "application/x-www-form-urlencoded",
                                    "client_id": CLIENTID,
                                    "client_secret": CLIENTSECRET,
                                    "scope": "api_labonneboitev1"})
        if token.status_code == 200:
            try:
                token = token.json()['access_token']
                req = requests.get("https://api.emploi-store.fr/partenaire/labonneboite/v1/company/",
                                   params={"distance": "50", "page_size": "100",
                                           "latitude": float(user_info.latitude),
                                           "longitude": float(user_info.longitude),
                                           "rome_codes": user_info.job_code.code, "page": 1},
                                   headers={"Authorization": "Bearer " + token}).json()
                companies = req['companies']
                companies_count = req['companies_count']
                saved_companies = Company.objects.filter(users__in=[request.user])
            except json.JSONDecodeError as e:
                print(e)
                return render(request, '500.html')
        else:
            return render(request, '500.html')

        context = {
            'companies': companies,
            'companies_count': companies_count,
            'nbPage': 1,
            'hasChosedJob': True if user_info.job_code is not None else False,
            'hasAddress': True if user_info.address is not None else False,
            'user': request.user,
            'savedCompanies': [comp.siret for comp in saved_companies],
            'jobs': TradeToRomeCode.objects.filter(job_code=user_info.job_code)[:3],
        }
        return render(request, 'main_platform/search.html', context)
    else:
        return render(request, 'main_platform/error.html')


@login_required
def account(request):
    """
    Account page, displaying information about the user
    """
    user = User.objects.get(email=request.user.email)
    user_info = UserInfos.objects.filter(user=user)[0]
    context = {
        'pseudo': user.username,
        'email': user.email,
        'address': user_info.address if user_info.address else "Aucune",
        'form': ChangeAddressForm(request.POST),
        'hasChosedJob': True if user_info.job_code is not None else False,
        'hasAddress': True if user_info.address is not None else False,
    }
    if user_info.job_code is not None:
        context['jobs'] = TradeToRomeCode.objects.filter(job_code=user_info.job_code)

    return render(request, 'main_platform/account.html', context)


@login_required
def updateAddress(request):
    """
    Modify address on user_info
    """
    user_info = UserInfos.objects.filter(user=request.user)[0]
    user_info.address = request.POST.get('addressInput')
    user_info.latitude = request.POST.get('latitude')
    user_info.longitude = request.POST.get('longitude')
    user_info.save(0)
    return redirect('main_platform:account')


@login_required
def choseJob(request):
    """
    Job choice page
    """
    user_info = UserInfos.objects.filter(user=request.user)[0]
    name = request.GET.get('name')
    context = {
        'jobs': TradeToRomeCode.objects.filter(job_name__istartswith=name),
        'hasChosedJob': True if user_info.job_code is not None else False,
        'hasAddress': True if user_info.address is not None else False,
        'search': request.GET.get('name')
    }
    return render(request, 'main_platform/choseJob.html', context)


@login_required
def chosedJob(request):
    """
    Save job then redirect user
    """
    code = request.GET.get('code')
    user_info = UserInfos.objects.filter(user=request.user)[0]
    user_info.job_code = RomeCode.objects.filter(code=code)[0]
    user_info.save(0)
    return redirect('main_platform:searchCompany')


@login_required
def deleteCompany(request):
    """
    Delete saved company
    """
    with transaction.atomic():
        try:
            user = request.user
            siret = request.POST.get('siret')
            selectedCompany = Company.objects.filter(siret=siret)[0]
            selectedCompany.users.remove(user)
            if selectedCompany.users.count() == 0:
                selectedCompany.delete()
        except Exception as e:
            print(e)

    return HttpResponseRedirect(request.path_info)


class SavedCompaniesListView(ListView):
    """
    Display saved companies
    """
    template_name = 'main_platform/savedCompanies.html'
    context_object_name = 'companies'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        user_info = UserInfos.objects.filter(user=self.request.user)[0]
        context['hasChosedJob'] = True if user_info.job_code is not None else False
        context['hasAddress'] = True if user_info.address is not None else False
        return context

    def get_queryset(self):
        return Company.objects.filter(users__in=[self.request.user]).all()
