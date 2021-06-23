from django.conf.urls import url

from . import views
from .views import SavedCompaniesListView

app_name = "main_platform"

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # url(r'^account/$', views.account, name='account'),
    url(r'^registrationPage/$', views.registrationPage, name='registrationPage'),
    url(r'^registration/$', views.registration, name='registration'),
    # url(r'^authenticationPage/$', views.authenticationPage, name='authenticationPage'),
    # url(r'^authentication/$', views.connect, name='authentication'),
    # url(r'^disconnect/$', views.disconnect, name='disconnection'),
    url(r'^account/$', views.account, name='account'),
    url(r'^updateAddress/$', views.updateAddress, name='updateAddress'),
    url(r'^choseJob/$', views.choseJob, name='choseJob'),
    url(r'^chosedJob/$', views.chosedJob, name='chosedJob'),
    url(r'^searchCompany/$', views.searchCompany, name='searchCompany'),
    url(r'^saveCompany/$', views.saveCompany, name='saveCompany'),
    url(r'^deleteCompany/$', views.deleteCompany, name='deleteCompany'),
    url(r'^savedCompanies/$', SavedCompaniesListView.as_view(), name='savedCompanies'),
]
