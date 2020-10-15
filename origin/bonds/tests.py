from rest_framework.test import APISimpleTestCase, APITestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.db import models
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from bonds.models import Bond

client = APIClient()

def getBondRequests():
    a = {
            'isin' : "FR0000131104",
            'size' : 100000,
            'currency' : "EUR",
            'maturity' : "2025-02-28",
            'lei' : "R0MUWSFPU8MPRO8K5P83"
        }

    b = {
            'isin' : "AB0000123345",
            'size' : 20000000,
            'currency' : "GBP",
            'maturity' : "2023-04-14",
            'lei' : "261700K5E45DJCF5Z735"
        }
    return a, b

def getCompletedBonds():
    a = {
            'isin' : "FR0000131104",
            'size' : 100000,
            'currency' : "EUR",
            'maturity' : "2025-02-28",
            'lei' : "R0MUWSFPU8MPRO8K5P83",
            'legal_name' : 'BNP PARIBAS'
        }

    b = {
            'isin' : "AB0000123345",
            'size' : 20000000,
            'currency' : "GBP",
            'maturity' : "2023-04-14",
            'lei' : "261700K5E45DJCF5Z735",
            'legal_name' : 'APIR SYSTEMS LIMITED'
        }
    return a, b

def getEmptyBond():
    a = {
            'isin' : "",
            'size' : 0,
            'currency' : "",
            'maturity' : "",
            'lei' : "",
        }

class HomePage(APISimpleTestCase):
    def test_root(self):
        resp = self.client.get("")
        assert resp.status_code == 200

class Authentication(APITestCase):
    def test_unauthorised_access(self):
        resp = self.client.get(reverse("bond_api"))
        msg = eval(resp.content.decode('utf-8'))['detail']
        assert resp.status_code == 403 and msg == 'Authentication credentials were not provided.'

    def setUp(self):
        self.credentials1 = {
            'username': 'testuser1',
            'password': 'secret'}
        User.objects.create_user(**self.credentials1)
        self.credentials2 = {
            'username': 'testuser2',
            'password': 'secret'}
        User.objects.create_user(**self.credentials2)

    def test_login(self):
        # send login data
        resp = self.client.post('/api-auth/login/?next=/bonds/', self.credentials1, follow=True)
        assert resp.status_code == 200

    def test_bond_access(self):
        bond1, bond2 = getBondRequests()
        completedBond1, completedBond2 = getCompletedBonds()
        # post bond from one user
        self.client.post('/api-auth/login/?next=/bonds/', self.credentials1, follow=True)
        self.client.post(reverse("bond_api"), bond1, follow=True)
        # post bond from other user
        self.client.post('/api-auth/login/?next=/bonds/', self.credentials2, follow=True)
        self.client.post(reverse("bond_api"), bond2, follow=True)
        # login as first user
        self.client.post('/api-auth/login/?next=/bonds/', self.credentials1, follow=True)
        resp = self.client.get(reverse("bond_api"))
        returnedBond = eval(resp.content.decode('utf-8'))
        # check only first users bond returned
        assert returnedBond == [completedBond1]


class BondAPI(APITestCase):

    def setUp(self):
        self.credentials1 = {
            'username': 'testuser1',
            'password': 'secret'}
        User.objects.create_user(**self.credentials1)
        self.credentials2 = {
            'username': 'testuser2',
            'password': 'secret'}
        User.objects.create_user(**self.credentials2)

    def test_post_bond(self):
        bond1, bond2 = getBondRequests()
        self.client.post('/api-auth/login/?next=/bonds/', self.credentials1, follow=True)
        resp = self.client.post(reverse("bond_api"), bond1, follow=True)
        assert resp.status_code == 201

    def test_bond_legal_name_fill(self):
        bond1, bond2 = getBondRequests()
        completedBond1, completedBond2 = getCompletedBonds()
        self.client.post('/api-auth/login/?next=/bonds/', self.credentials1, follow=True)
        self.client.post(reverse("bond_api"), bond1, follow=True)
        resp = self.client.get(reverse("bond_api"))
        [returnedBond] = eval(resp.content.decode('utf-8'))
        assert returnedBond['legal_name']==completedBond1['legal_name']

    def test_multiple_bond_post(self):
        bond1, bond2 = getBondRequests()
        completedBond1, completedBond2 = getCompletedBonds()
        self.client.post('/api-auth/login/?next=/bonds/', self.credentials1, follow=True)
        self.client.post(reverse("bond_api"), bond1, follow=True)
        self.client.post(reverse("bond_api"), bond2, follow=True)
        resp = self.client.get(reverse("bond_api"))
        returnedBond = eval(resp.content.decode('utf-8'))
        assert returnedBond==[completedBond1,completedBond2]

    def test_bond_url_filter(self):
        bond1, bond2 = getBondRequests()
        completedBond1, completedBond2 = getCompletedBonds()
        self.client.post('/api-auth/login/?next=/bonds/', self.credentials1, follow=True)
        self.client.post(reverse("bond_api"), bond1, follow=True)
        self.client.post(reverse("bond_api"), bond2, follow=True)
        resp = self.client.get('/bonds/?currency=GBP')
        returnedBond = eval(resp.content.decode('utf-8'))
        assert returnedBond==[completedBond2]

    def test_invalid_isin_post(self):
        bond1, bond2 = getBondRequests()
        bond1['isin'] = 'broken'
        self.client.post('/api-auth/login/?next=/bonds/', self.credentials1, follow=True)
        resp = self.client.post(reverse("bond_api"), bond1, follow=True)
        [msg] = eval(resp.content.decode('utf-8'))['isin']
        assert resp.status_code == 400 and msg == 'Error: ISIN is not of length 12'

    def test_invalid_size_post(self):
        bond1, bond2 = getBondRequests()
        bond1['size'] = -1
        self.client.post('/api-auth/login/?next=/bonds/', self.credentials1, follow=True)
        resp = self.client.post(reverse("bond_api"), bond1, follow=True)
        [msg] = eval(resp.content.decode('utf-8'))['size']
        assert resp.status_code == 400 and msg == 'Error: Size must be at least 1'

    def test_invalid_currency_post(self):
        bond1, bond2 = getBondRequests()
        bond1['currency'] = 'BR'
        self.client.post('/api-auth/login/?next=/bonds/', self.credentials1, follow=True)
        resp = self.client.post(reverse("bond_api"), bond1, follow=True)
        [msg] = eval(resp.content.decode('utf-8'))['currency']
        assert resp.status_code == 400 and msg == 'Error: Currency is not of length 3'

    def test_invalid_lei_post(self):
        bond1, bond2 = getBondRequests()
        bond1['lei'] = 'broken'
        self.client.post('/api-auth/login/?next=/bonds/', self.credentials1, follow=True)
        resp = self.client.post(reverse("bond_api"), bond1, follow=True)
        [msg] = eval(resp.content.decode('utf-8'))['lei']
        assert resp.status_code == 400 and msg == 'Error: LEI is not of length 20'

    def test_invalid_legal_name_match(self):
        bond1, bond2 = getBondRequests()
        bond1['lei'] = 'XXXXqSFPU8MPRO8K5P83'
        self.client.post('/api-auth/login/?next=/bonds/', self.credentials1, follow=True)
        resp = self.client.post(reverse("bond_api"), bond1, follow=True)
        [msg] = eval(resp.content.decode('utf-8'))
        assert resp.status_code == 400 and msg == 'Error: Legal Name corresponding to LEI could not be found through the GLIEF API'

    def test_empty_bond_post(self):
        emptybond = getEmptyBond()
        self.client.post('/api-auth/login/?next=/bonds/', self.credentials1, follow=True)
        resp = self.client.post(reverse("bond_api"), emptybond, follow=True)
        msg = eval(resp.content.decode('utf-8'))
        errorset = {'isin': ['This field is required.'], 'currency': ['This field is required.'], 'maturity': ['This field is required.'], 'lei': ['This field is required.']}
        assert resp.status_code == 400 and msg == errorset
