import secrets

from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from main.models import Project


class TokenAuthenticationAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = secrets.token_urlsafe(24)
        cls.owner = User.objects.create_superuser('token-owner', 'token-owner@example.com', cls.password)
        cls.regular = User.objects.create_user('token-regular', password=cls.password)
        cls.project = Project.objects.create(title='Token project', description='Test project', tech_stack='Django')

    def setUp(self):
        self.list_url = reverse('api:project-list')
        self.detail_url = reverse('api:project-detail', args=[self.project.pk])
        self.login_url = reverse('api:api_token_auth')
        self.logout_url = reverse('api:api_logout')
        self.payload = {'title': 'Created with token', 'description': 'Test', 'tech_stack': 'Django'}

    def login_token(self, user, client=None):
        client = client or self.client
        response = client.post(self.login_url, {'username': user.username, 'password': self.password}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('token'))
        client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['token'])
        return response.data['token']

    def test_public_get_and_guest_write_challenge(self):
        self.assertEqual(self.client.get(self.list_url).status_code, 200)
        self.assertEqual(self.client.get(self.detail_url).status_code, 200)
        response = self.client.post(self.list_url, self.payload, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['WWW-Authenticate'], 'Token')
        self.assertEqual(Project.objects.count(), 1)

    def test_superuser_token_creates_and_updates_without_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        self.login_token(self.owner, client)
        self.assertEqual(client.post(self.list_url, self.payload, format='json').status_code, 201)
        self.assertEqual(client.patch(self.detail_url, {'title': 'Changed'}, format='json').status_code, 200)
        self.assertEqual(Project.objects.count(), 2)

    def test_regular_token_cannot_create_update_or_delete(self):
        self.login_token(self.regular)
        self.assertEqual(self.client.post(self.list_url, self.payload, format='json').status_code, 403)
        self.assertEqual(self.client.patch(self.detail_url, {'title': 'Denied'}, format='json').status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

    def test_logout_revokes_only_callers_token(self):
        other = Token.objects.create(user=self.regular)
        key = self.login_token(self.owner)
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b'')
        self.assertFalse(Token.objects.filter(user=self.owner).exists())
        self.assertTrue(Token.objects.filter(pk=other.pk).exists())
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + key)
        self.assertEqual(self.client.post(self.list_url, self.payload, format='json').status_code, 401)
        self.assertEqual(self.client.post(self.logout_url).status_code, 401)
        self.client.credentials()
        self.assertEqual(self.client.get(self.list_url).status_code, 200)

    def test_login_rejects_invalid_credentials_and_logout_requires_authentication(self):
        response = self.client.post(self.login_url, {'username': self.owner.username, 'password': 'invalid'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Token.objects.filter(user=self.owner).exists())
        self.assertEqual(self.client.post(self.logout_url).status_code, 401)
        self.assertEqual(self.client.get(self.logout_url).status_code, 401)
        self.assertEqual(self.client.get(self.login_url).status_code, 405)

    @override_settings(CORS_ALLOW_ALL_ORIGINS=True)
    def test_local_cors_preflight_allows_token_header(self):
        response = self.client.options(self.list_url, HTTP_ORIGIN='http://localhost:54321',
            HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST', HTTP_ACCESS_CONTROL_REQUEST_HEADERS='authorization,content-type')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Access-Control-Allow-Origin'], '*')
        self.assertIn('authorization', response['Access-Control-Allow-Headers'])

    @override_settings(CORS_ALLOW_ALL_ORIGINS=False, CORS_ALLOWED_ORIGINS=['https://portfolio.example.com'])
    def test_production_cors_restricts_origins(self):
        response = self.client.get(self.list_url, HTTP_ORIGIN='https://portfolio.example.com')
        self.assertEqual(response['Access-Control-Allow-Origin'], 'https://portfolio.example.com')
        response = self.client.get(self.list_url, HTTP_ORIGIN='https://unlisted.example.com')
        self.assertNotIn('Access-Control-Allow-Origin', response)
