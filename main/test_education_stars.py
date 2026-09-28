import uuid

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse

from main.models import Education


class EducationStarTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = User.objects.create_user("member", email="private@example.com")
        cls.editor = User.objects.create_user("editor")
        cls.editor.groups.add(Group.objects.create(name="Editor"))
        cls.owner = User.objects.create_superuser("owner", "owner@example.com", "Test-password-482!")
        cls.education = Education.objects.create(title="Degree", institution="UI", year="2026")

    def url(self):
        return reverse("main:toggle_education_star", args=[self.education.pk])

    def test_guest_redirects_to_login(self):
        self.assertRedirects(self.client.post(self.url()), "/login/?next=" + self.url())
        self.assertEqual(self.education.starred_by.count(), 0)

    def test_all_authenticated_roles_can_star_and_unstar_independently(self):
        for user in [self.member, self.editor, self.owner]:
            self.client.force_login(user)
            self.assertRedirects(self.client.post(self.url()), reverse("main:show_education"))
            self.assertTrue(self.education.starred_by.filter(pk=user.pk).exists())
            self.assertIn(self.education, user.starred_educations.all())
        self.assertEqual(self.education.starred_by.count(), 3)
        self.client.post(self.url(), {"user_id": self.member.pk})
        self.assertFalse(self.education.starred_by.filter(pk=self.owner.pk).exists())
        self.assertTrue(self.education.starred_by.filter(pk=self.member.pk).exists())
        self.assertEqual(self.education.starred_by.count(), 2)

    def test_relation_does_not_allow_duplicate_stars(self):
        self.education.starred_by.add(self.member)
        self.education.starred_by.add(self.member)
        self.assertEqual(self.education.starred_by.count(), 1)

    def test_only_post_is_accepted(self):
        self.client.force_login(self.member)
        for method in ["get", "put", "patch", "delete", "head"]:
            self.assertEqual(getattr(self.client, method)(self.url()).status_code, 405)
        self.assertEqual(self.education.starred_by.count(), 0)
        self.assertEqual(self.client.post(reverse("main:toggle_education_star", args=[uuid.uuid4()])).status_code, 404)

    def test_json_exposes_only_public_fields_and_usernames(self):
        self.education.starred_by.add(self.member)
        response = self.client.get(reverse("main:get_education_json"))
        self.assertEqual(response.status_code, 200)
        fields = response.json()[0]["fields"]
        self.assertEqual(set(fields), {"title", "institution", "year", "category", "description", "image_url", "starred_by"})
        self.assertEqual(fields["starred_by"], [["member"]])
        self.assertNotContains(response, "private@example.com")
        self.assertNotContains(response, "password")

    def test_csrf_protects_star_create_update_delete(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        for url in [self.url(), reverse("main:create_education"),
                    reverse("main:edit_education", args=[self.education.pk]),
                    reverse("main:delete_education", args=[self.education.pk])]:
            self.assertEqual(client.post(url).status_code, 403)
        self.assertTrue(Education.objects.filter(pk=self.education.pk).exists())
        self.assertEqual(self.education.starred_by.count(), 0)
        client.get(reverse("main:login"))
        response = client.post(self.url(), {"csrfmiddlewaretoken": client.cookies["csrftoken"].value})
        self.assertRedirects(response, reverse("main:show_education"))
        self.assertEqual(self.education.starred_by.count(), 1)
