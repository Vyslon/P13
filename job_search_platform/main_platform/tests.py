import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.chrome.options import Options
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase, LiveServerTestCase
from django.urls import reverse
from selenium.webdriver.common.by import By
from .models import UserInfos, RomeCode, TradeToRomeCode, Company
from decimal import Decimal
from selenium import webdriver


class IndexPageTestCase(TestCase):

    def test_index_page(self):
        response = self.client.get(reverse('main_platform:index'))
        self.assertEqual(response.status_code, 302)


class AccountRegistrationAuthenticationPageTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user('temporary', 'temporary@gmail.com',
                                        'temporary')
        UserInfos.objects.create(user=user)

    def test_account_page_returns_200(self):
        self.client.login(username='temporary', password='temporary')
        response = self.client.get(reverse('main_platform:account'))
        self.assertEqual(response.status_code, 200)

    def test_account_page_returns_302(self):
        response = self.client.get(reverse('main_platform:account'))
        self.assertEqual(response.status_code, 302)

    def test_registration_page_returns_200(self):
        response = self.client.get(reverse('main_platform:registrationPage'))
        self.assertEqual(response.status_code, 200)

    def test_registration_page_returns_302(self):
        self.client.login(username='temporary', password='temporary')
        response = self.client.get(reverse('main_platform:registrationPage'))
        self.assertEqual(response.status_code, 302)

    def test_registration(self):
        response = self.client.post(reverse('main_platform:registration'), {
            'password': 'test1234',
            'email': 'test@gmail.com',
            'username': 'test'})
        self.assertNotEqual(User.objects.filter(email__exact='test@gmail.com').first(), None)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(response.wsgi_request.user.username, 'test')
        self.assertEqual(response.wsgi_request.user.email, 'test@gmail.com')

    def test_connection(self):
        response = self.client.post(reverse('login'), {
            'username': 'temporary',
            'password': 'temporary'
        })

    def test_authentication_page_returns_200(self):
        response = self.client.get(reverse(
            'login'))
        self.assertEqual(response.status_code, 200)

    def test_authentication_page_returns_302(self):
        self.client.login(username='temporary', password='temporary')
        response = self.client.get(reverse(
            'login'))
        self.assertEqual(response.status_code, 302)

    def test_disconnection_connected_page_returns_302(self):
        self.client.login(username='temporary', password='temporary')
        response = self.client.get(reverse(
            'logout'))
        self.assertEqual(response.status_code, 302)

    def test_disconnection_disconnected_page_returns_302(self):
        response = self.client.get(reverse(
            'logout'))
        self.assertEqual(response.status_code, 302)


class SaveCompanyPageTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user('temporary', 'temporary@gmail.com',
                                        'temporary')
        UserInfos.objects.create(user=user)
        Company.objects.create(name='Leclerc',
                               headcount_text='2 à 5 salariés',
                               contact_mode='Se présenter spontanément',
                               url='https://labonneboite.pole-emploi.fr/32615976100021/details?rome_code=D1101'
                                   '&utm_medium=web&utm_source=api__emploi_store_dev&utm_campaign',
                               alternance='True',
                               siret='222 333 666 11111')

    # test that a new company is saved by a user
    def test_save_new_company(self):
        user = authenticate(username='temporary', password='temporary')
        self.client.login(username='temporary', password='temporary')
        companySavedByUserBefore = Company.objects.filter(users__in=[user]).count()
        response = self.client.post(reverse('main_platform:saveCompany'), {
            'name': 'Auchan',
            'headcount_text': '20 à 49 salariés',
            'contact_mode': 'Se présenter spontanément',
            'url': 'https://labonneboite.pole-emploi.fr/32615976100021/details?rome_code=D1101&utm_medium=web'
                   '&utm_source=api__emploi_store_dev&utm_campaign=api__emploi_store_dev__jsearch',
            'alternance': 'False',
            'siret': '444 555 888 00000',

        })

        self.assertEqual(Company.objects.filter(users__in=[user]).count(), companySavedByUserBefore + 1)

    # test that an already existing company is saved by a user
    def test_save_existing_company(self):
        user = authenticate(username='temporary', password='temporary')
        self.client.login(username='temporary', password='temporary')
        companySavedByUserBefore = Company.objects.filter(users__in=[user]).count()
        companyCountBefore = Company.objects.count()
        response = self.client.post(reverse('main_platform:saveCompany'), {
            'name': 'Leclerc',
            'headcount_text': '2 à 5 salariés',
            'contact_mode': 'Se présenter spontanément',
            'url': 'https://labonneboite.pole-emploi.fr/32615976100021/details?rome_code=D1101&utm_medium=web'
                   '&utm_source=api__emploi_store_dev&utm_campaign',
            'alternance': 'True',
            'siret': '222 333 666 11111',

        })

        self.assertEqual(Company.objects.filter(users__in=[user]).count(), companySavedByUserBefore + 1)
        self.assertEqual(Company.objects.count(), companyCountBefore)


class UpdateJobAddressTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user('temporary', 'temporary@gmail.com',
                                        'temporary')
        UserInfos.objects.create(user=user, address='address', latitude='45.7595253', longitude='45.7595253')

    def test_update_address(self):
        user = authenticate(username='temporary', password='temporary')
        self.client.login(username='temporary', password='temporary')
        user_info = UserInfos.objects.filter(user=user)[0]
        addressInput = 'address'
        latitude = '55.7595264'
        longitude = '55.7595264'
        response = self.client.post(reverse('main_platform:updateAddress'), {
            'addressInput': addressInput,
            'latitude': latitude,
            'longitude': longitude,
        })
        user_info = UserInfos.objects.filter(user=user)[0]
        self.assertEqual(user_info.address, addressInput)
        self.assertEqual(user_info.latitude, Decimal(latitude))
        self.assertEqual(user_info.longitude, Decimal(longitude))

    def test_update_job(self):
        user = authenticate(username='temporary', password='temporary')
        self.client.login(username='temporary', password='temporary')
        user_info = UserInfos.objects.filter(user=user)[0]
        test_rome_code = RomeCode.objects.create(code='ABC24')
        TradeToRomeCode.objects.create(job_name='test', job_code=test_rome_code)
        response = self.client.get(reverse('main_platform:chosedJob'), {
            'code': 'ABC24',
        })

        user_info = UserInfos.objects.filter(user=user)[0]

        self.assertEqual(user_info.job_code.code, 'ABC24')


class SavedCompaniesTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user('temporary', 'temporary@gmail.com',
                                        'temporary')
        user2 = User.objects.create_user('temporary2', 'temporary2@gmail.com',
                                         'temporary2')
        user_info = UserInfos.objects.create(user=user, address='address', latitude='45.7595253',
                                             longitude='45.7595253')
        test_rome_code = RomeCode.objects.create(code='ABC24')
        TradeToRomeCode.objects.create(job_name='test', job_code=test_rome_code)
        user_info.job_code = test_rome_code
        UserInfos.objects.create(user=user2)
        myCompany = Company.objects.create(name='Leclerc',
                                           headcount_text='2 à 5 salariés',
                                           contact_mode='Se présenter spontanément',
                                           url='https://labonneboite.pole-emploi.fr/32615976100021/details?rome_code'
                                               '=D1101&utm_medium=web&utm_source=api__emploi_store_dev&utm_campaign',
                                           alternance='True',
                                           siret='222 333 666 11111')
        myCompany.users.add(user)
        myCompany.users.add(user2)

    def test_delete_saved_company_user_remaining(self):
        user = authenticate(username='temporary', password='temporary')
        self.client.login(username='temporary', password='temporary')
        response = self.client.post(reverse('main_platform:deleteCompany'), {
            'siret': '222 333 666 11111',
        })

        self.assertEqual(Company.objects.filter(siret='222 333 666 11111')[0].users.count(), 1)

    def test_delete_saved_company(self):
        user = authenticate(username='temporary', password='temporary')
        self.client.login(username='temporary', password='temporary')
        testCompany = Company.objects.create(name='test',
                                             headcount_text='2 à 5 salariés',
                                             contact_mode='Se présenter spontanément',
                                             url='https://url.com',
                                             alternance='True',
                                             siret='000')
        testCompany.users.add(user)

        self.assertEqual(Company.objects.filter(siret='000').count(), 1)
        self.assertEqual(testCompany.users.count(), 1)

        response = self.client.post(reverse('main_platform:deleteCompany'), {
            'siret': '000',
        })

        self.assertEqual(Company.objects.filter(siret='000').count(), 0)


# TODO : monkeypatch
# class SearchCompanyTestCase(TestCase):
#     def setUp(self):
#         user = User.objects.create_user('temporarySC', 'temporarySC@gmail.com',
#                                         'temporarySC')
#
#         user_info = UserInfos.objects.create(user=user, address='address', latitude='45.7595253',
#                                              longitude='45.7595253')
#         test_rome_code = RomeCode.objects.create(code='ABC24')
#         TradeToRomeCode.objects.create(job_name='test', job_code=test_rome_code)
#         user_info.job_code = test_rome_code
#         user = authenticate(username='temporarySC', password='temporarySC')
#
#     def test_api_valid_token(self, monkeypatch):
#         class Token:
#             status_code = 200
#             content = json.dumps({
#                 "access_token": "wehqh8238eg2q8ge8"
#             }).encode()
#
#         data = json.dumps({
#             "companies": [{
#                 "distance": 2,
#                 "headcount_text": "6 à 9 salariés",
#                 "lat": 48.97609,
#                 "city": "PAGNY-SUR-MOSELLE",
#                 "naf": "4711D",
#                 "name": "LIDL",
#                 "naf_text": "Supermarchés",
#                 "lon": 5.99792,
#                 "siret": "34326262214546"
#             }],
#             "companies_count": 1}).encode()
#
#         def mockreturnToken(request):
#             return Token
#
#         def mockreturnData(request):
#             return data
#
#         monkeypatch.setattr(requests, 'post', mockreturnToken)
#         monkeypatch.setattr(requests, 'get', mockreturnData)
#
#         response = self.client.post(reverse('main_platform:searchCompany'))
#         self.assertEqual(response.context['companies'], [{'distance': 2, 'headcount_text': '6 à 9 salariés',
#                                                           'lat': 48.97609, 'city': 'PAGNY-SUR-MOSELLE', 'naf': '4711D',
#                                                           'name': 'LIDL', 'naf_text': 'Supermarchés', 'lon': 5.99792,
#                                                           'siret': '34326262214546'}])
#         self.assertEqual(response.context['companies_count'], 1)


class UserUseCaseTest(StaticLiveServerTestCase):
    fixtures = ['datadump.json']

    def testform(self):
        chrome_options = Options()
        chrome_options.add_argument("--enable-javascript")
        selenium = webdriver.Chrome(chrome_options=chrome_options)
        # selenium.get('http://127.0.0.1:8000/')
        selenium.get(self.live_server_url + '/main/registrationPage/')
        user_username = selenium.find_element_by_id('id_username')
        user_username.send_keys('testuser')
        user_mail = selenium.find_element_by_id('id_email')
        user_mail.send_keys('testuser@gmail.com')
        user_password = selenium.find_element_by_id('id_password')
        user_password.send_keys('testuser')
        selenium.find_element_by_id('id_checkbox').click()

        # submit = selenium.find_element_by_id('id_submit')
        # selenium.find_element_by_id('id_submit').click()
        selenium.find_element_by_id('id_submit').click()

        # user = User.objects.filter(email__exact='testuser@gmail.com').first()
        # user_info = UserInfos.objects.filter(user=user)[0]
        # user_info.address = 'Place Bellecour, Lyon, France'
        # user_info.latitude = '45.7568283'
        # user_info.longitude = '4.8315189'
        # user_info.save()
        # selenium.refresh()

        assert 'testuser' in selenium.page_source
        assert 'testuser@gmail.com' in selenium.page_source
        assert 'Adresse sauvegardée' in selenium.page_source

        # TODO : select Address ...
        """
        It is not possible to gave an address manually, the google maps autocompletion is not working with selenium
        """

        address = selenium.find_element_by_id('addressInput')
        address.send_keys('place bellecour')
        selenium.find_element_by_id('addressInput').click()
        selenium.implicitly_wait(10)
        selenium.find_element(By.XPATH, "//span[.='Lyon, France']").click()
        selenium.implicitly_wait(10)
        time.sleep(10)
        selenium.find_element_by_id('changeAddress').click()
        time.sleep(10)
        user_wanted_job = selenium.find_element_by_id('íd_jobwanted')
        user_wanted_job.send_keys('boulanger')
        selenium.find_element_by_id('id_jobwantedsubmit').click()
        selenium.find_element_by_partial_link_text("Boulanger").click()
        time.sleep(12)
        selenium.find_element(By.XPATH, "//table/tbody/tr[1]/td[1]/form/input[2]").click()
        selenium.find_element_by_id('id_savedCompanies').click()
        time.sleep(12)

        assert len(selenium.find_elements_by_xpath("//input[contains(@class, 'delete')]")) >= 1

        selenium.find_element_by_xpath("//input[contains(@class, 'delete')]").click()

        assert len(selenium.find_elements_by_xpath("//input[contains(@class, 'delete')]")) == 0
