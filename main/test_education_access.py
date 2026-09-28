from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from main.models import Education


class EducationAccessTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = User.objects.create_user("reader")
        cls.owner = User.objects.create_superuser("owner", "owner@example.com", "Test-password-482!")
        cls.education = Education.objects.create(
            title="Information Systems", institution="Universitas Indonesia",
            year="2026", category="formal",
        )

    def actions(self):
        return [
            reverse("main:create_education"),
            reverse("main:edit_education", args=[self.education.pk]),
            reverse("main:delete_education", args=[self.education.pk]),
        ]

    def payload(self):
        return {"title": "Updated degree", "institution": "UI", "year": "2026", "category": "formal"}

    def test_guest_redirected_without_mutation(self):
        for url in self.actions():
            for method in [self.client.get, self.client.post]:
                self.assertRedirects(method(url), "/login/?next=" + url)
        self.education.refresh_from_db()
        self.assertEqual(self.education.title, "Information Systems")
        self.assertEqual(Education.objects.count(), 1)

    def test_regular_user_forbidden_for_all_writes(self):
        self.client.force_login(self.member)
        for url in self.actions():
            for method in [self.client.get, self.client.post]:
                self.assertEqual(method(url, self.payload()).status_code, 403)
        self.education.refresh_from_db()
        self.assertEqual(self.education.title, "Information Systems")
        self.assertEqual(Education.objects.count(), 1)

    def test_superuser_can_create_update_and_delete(self):
        self.client.force_login(self.owner)
        create, edit, delete = self.actions()
        for url in [create, edit]:
            self.assertEqual(self.client.get(url).status_code, 200)
            self.assertRedirects(self.client.post(url, self.payload()), reverse("main:show_education"))
        self.education.refresh_from_db()
        self.assertEqual(self.education.title, "Updated degree")
        self.assertEqual(Education.objects.count(), 2)
        self.client.get(delete)
        self.assertTrue(Education.objects.filter(pk=self.education.pk).exists())
        self.assertRedirects(self.client.post(delete), reverse("main:show_education"))
        self.assertFalse(Education.objects.filter(pk=self.education.pk).exists())

    def test_public_education_and_json_remain_readable(self):
        for name in ["show_education", "get_education_json"]:
            self.assertContains(self.client.get(reverse("main:" + name)), "Information Systems")
