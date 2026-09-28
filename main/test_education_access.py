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

    def test_editor_can_only_update(self):
        from django.contrib.auth.models import Group
        self.member.groups.add(Group.objects.create(name="Editor"))
        self.client.force_login(self.member)
        create, edit, delete = self.actions()
        self.assertEqual(self.client.get(edit).status_code, 200)
        self.assertRedirects(self.client.post(edit, self.payload()), reverse("main:show_education"))
        self.education.refresh_from_db()
        self.assertEqual(self.education.title, "Updated degree")
        for url in [create, delete]:
            for method in [self.client.get, self.client.post]:
                self.assertEqual(method(url, self.payload()).status_code, 403)
        self.assertEqual(Education.objects.count(), 1)

    def test_editor_membership_removal_revokes_edit_access(self):
        from django.contrib.auth.models import Group
        group = Group.objects.create(name="Editor")
        self.member.groups.add(group)
        self.client.force_login(self.member)
        edit = self.actions()[1]
        self.assertEqual(self.client.get(edit).status_code, 200)
        self.member.groups.remove(group)
        self.assertEqual(self.client.post(edit, self.payload()).status_code, 403)

    def test_staff_or_similarly_named_group_is_not_editor(self):
        from django.contrib.auth.models import Group
        self.member.is_staff = True
        self.member.save()
        self.member.groups.add(Group.objects.create(name="editor"))
        self.client.force_login(self.member)
        self.assertEqual(self.client.post(self.actions()[1], self.payload()).status_code, 403)

    def test_admin_exposes_user_and_group_management_to_owner(self):
        self.client.force_login(self.owner)
        for url in ["admin:auth_group_add", "admin:auth_user_change"]:
            args = [self.member.pk] if url.endswith("change") else []
            self.assertEqual(self.client.get(reverse(url, args=args)).status_code, 200)

    def test_controls_follow_each_role(self):
        from django.contrib.auth.models import Group
        editor = User.objects.create_user("editor")
        editor.groups.add(Group.objects.create(name="Editor"))
        create, edit, delete = self.actions()
        for user in [None, self.member, editor, self.owner]:
            with self.subTest(user=user):
                self.client.logout()
                if user:
                    self.client.force_login(user)
                response = self.client.get(reverse("main:show_education"))
                for url, allowed in [(create, user == self.owner), (edit, user in [editor, self.owner]), (delete, user == self.owner)]:
                    if allowed:
                        self.assertContains(response, url)
                    else:
                        self.assertNotContains(response, url)
                self.assertContains(response, reverse("main:toggle_education_star", args=[self.education.pk]))
