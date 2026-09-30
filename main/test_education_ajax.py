from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse

from main.forms import EducationForm
from main.models import Education


class EducationAjaxTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser('ajax-owner', 'owner@example.com', 'Test-password-482!')
        cls.member = User.objects.create_user('ajax-member')
        cls.editor = User.objects.create_user('ajax-editor')
        cls.editor.groups.add(Group.objects.create(name='Editor'))

    def setUp(self):
        self.url = reverse('main:create_education_ajax')
        self.payload = {'title': 'Degree', 'institution': 'UI', 'year': '2026', 'category': 'formal'}

    def test_only_superuser_can_create_and_only_via_post(self):
        for user in [None, self.member, self.editor, self.owner]:
            self.client.logout()
            if user:
                self.client.force_login(user)
            self.assertEqual(self.client.get(self.url).status_code, 405)
            response = self.client.post(self.url, self.payload)
            self.assertEqual(response.status_code, 201 if user == self.owner else 403)
            self.assertIn('message', response.json())
            if user == self.owner:
                self.assertTrue(Education.objects.filter(pk=response.json()['pk']).exists())
        self.assertEqual(Education.objects.count(), 1)

    def test_invalid_fields_and_tag_only_title_do_not_save(self):
        self.client.force_login(self.owner)
        for field, value in [('title', '   '), ('title', '<img src="x" onerror="alert(\'XSS!\')">'),
                             ('image_url', 'javascript:alert(1)'), ('category', 'unknown')]:
            response = self.client.post(self.url, {**self.payload, field: value})
            self.assertEqual(response.status_code, 400)
            self.assertIn(field, response.json()['errors'])
        self.assertEqual(Education.objects.count(), 0)

    def test_form_cleans_text_and_accepts_empty_description(self):
        form = EducationForm({**self.payload, 'title': '<b>Degree</b>',
                              'institution': '<i>UI</i>', 'year': '<b>2026</b>',
                              'description': '<p>Study</p>'})
        self.assertTrue(form.is_valid(), form.errors)
        for field, value in [('title', 'Degree'), ('institution', 'UI'), ('year', '2026'), ('description', 'Study')]:
            self.assertEqual(form.cleaned_data[field], value)
        form = EducationForm(self.payload)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['description'], '')

    def test_csrf_is_required_and_header_is_accepted(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(client.post(self.url, self.payload).status_code, 403)
        client.get(reverse('main:show_education'))
        response = client.post(self.url, self.payload, HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)
        self.assertEqual(response.status_code, 201)

    def test_modal_only_exists_for_superuser(self):
        for user in [None, self.member, self.editor, self.owner]:
            self.client.logout()
            if user:
                self.client.force_login(user)
            response = self.client.get(reverse('main:show_education'))
            self.assertIsInstance(response.context['form'], EducationForm)
            if user == self.owner:
                self.assertContains(response, 'id="education-form"')
                self.assertContains(response, 'popovertarget="add-education-modal"')
            else:
                self.assertNotContains(response, 'id="education-form"')
                self.assertNotContains(response, 'popovertarget="add-education-modal"')

    def test_legacy_create_and_edit_share_title_validation(self):
        self.client.force_login(self.owner)
        education = Education.objects.create(**self.payload)
        for url in [reverse('main:create_education'), reverse('main:edit_education', args=[education.pk])]:
            response = self.client.post(url, {**self.payload, 'title': '<img src="x">'})
            self.assertEqual(response.status_code, 200)
            self.assertIn('title', response.context['form'].errors)
        self.assertEqual(Education.objects.count(), 1)
        education.refresh_from_db()
        self.assertEqual(education.title, 'Degree')
