from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Education


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

##INI BUAT TEST BAGIAN EDUCATION

class EducationTest(TestCase):
    def setUp(self):
        self.edu = Education.objects.create(
            institution="Universitas Indonesia",
            title="S1 Sistem Informasi",
            category="formal",
            year="2024 - Sekarang",
            description="Fakultas Ilmu Komputer. Fokus pada sistem informasi dan AI.",
        )

    def test_education_url_is_accessible(self):
        response = self.client.get(reverse("main:show_education"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")

    def test_education_page_with_data(self):
        response = self.client.get(reverse("main:show_education"))
        self.assertNotIn("education_list", response.context)
        fields = self.client.get(reverse("main:get_education_json")).json()[0]["fields"]
        self.assertEqual(fields["title"], self.edu.title)
        self.assertEqual(fields["institution"], self.edu.institution)
        self.assertEqual(fields["category_display"], "Formal Education")

    def test_empty_education_page(self):
        Education.objects.all().delete()
        response = self.client.get(reverse("main:show_education"))
        self.assertContains(response, "Belum ada data pendidikan yang ditambahkan atau ditemukan.")


class AuthenticationTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_user("visitor", password="Test-password-482!")

    def test_register_hashes_password_without_logging_in(self):
        from django.contrib.auth.models import User
        response = self.client.post(reverse("main:register"), {
            "username": "newvisitor", "password1": "New-password-482!",
            "password2": "New-password-482!", "is_superuser": "true",
        }, follow=True)
        self.assertRedirects(response, reverse("main:login"))
        self.assertContains(response, "Akun berhasil dibuat")
        user = User.objects.get(username="newvisitor")
        self.assertTrue(user.check_password("New-password-482!"))
        self.assertFalse(user.is_superuser)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_registration_errors_do_not_create_accounts(self):
        from django.contrib.auth.models import User
        for username, confirmation in [("visitor", "New-password-482!"), ("newvisitor", "mismatch")]:
            with self.subTest(username=username):
                response = self.client.post(reverse("main:register"), {
                    "username": username, "password1": "New-password-482!",
                    "password2": confirmation,
                })
                self.assertTrue(response.context["form"].errors)
                self.assertContains(response, "errorlist")
                self.assertEqual(User.objects.count(), 1)

    def test_login_persists_across_pages_and_logout_keeps_account(self):
        response = self.client.post(reverse("main:login"), {
            "username": "visitor", "password": "wrong",
        })
        self.assertTrue(response.context["form"].non_field_errors())
        self.assertNotIn("_auth_user_id", self.client.session)
        response = self.client.post(reverse("main:login"), {
            "username": "visitor", "password": "Test-password-482!",
        })
        self.assertRedirects(response, reverse("main:show_main"))
        for page in ["show_main", "show_experience", "show_projects", "show_education"]:
            response = self.client.get(reverse("main:" + page))
            self.assertContains(response, '<span class="nav-user">visitor</span>')
            self.assertContains(response, reverse("main:logout"))
        response = self.client.get(reverse("main:logout"), follow=True)
        self.assertContains(response, 'href="/login/"')
        self.assertNotIn("_auth_user_id", self.client.session)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Test-password-482!"))

    def test_authentication_forms_require_csrf(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        for page in ["register", "login"]:
            response = client.get(reverse("main:" + page))
            self.assertContains(response, "csrfmiddlewaretoken")
            self.assertEqual(client.post(reverse("main:" + page), {}).status_code, 403)


class LoginCookieTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        User.objects.create_user("cookievisitor", password="Test-password-482!")

    def test_cookie_lifecycle(self):
        from unittest.mock import patch
        import datetime
        self.assertContains(self.client.get(reverse("main:show_main")), "Belum ada sesi login")
        with patch("main.views.timezone.localtime", return_value=datetime.datetime(2026, 9, 27, 20, 30, 45)):
            response = self.client.post(reverse("main:login"), {
                "username": "cookievisitor", "password": "Test-password-482!",
            })
        cookie = response.cookies["last_login"]
        self.assertEqual(cookie.value, "2026-09-27 20:30:45")
        self.assertEqual(cookie["max-age"], "")
        self.assertEqual(cookie["samesite"], "Lax")
        self.assertTrue(cookie["httponly"])
        self.assertIn("sessionid", response.cookies)
        self.assertContains(self.client.get(reverse("main:show_main")), cookie.value)
        response = self.client.get(reverse("main:logout"))
        self.assertEqual(response.cookies["last_login"]["max-age"], 0)
        self.assertEqual(response.cookies["sessionid"]["max-age"], 0)
        self.assertContains(self.client.get(reverse("main:show_main")), "Belum ada sesi login")

    def test_failed_login_does_not_issue_cookie(self):
        response = self.client.post(reverse("main:login"), {
            "username": "cookievisitor", "password": "wrong",
        })
        self.assertNotIn("last_login", response.cookies)

    def test_cookie_is_display_only_and_escaped(self):
        self.client.cookies["last_login"] = "<script>alert(1)</script>"
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, "&lt;script&gt;")
        self.assertFalse(response.context["user"].is_authenticated)


class ProjectAuthorizationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth.models import User
        from main.models import Project
        cls.member = User.objects.create_user("member")
        cls.other = User.objects.create_user("other")
        cls.owner = User.objects.create_superuser("owner", "owner@example.com", "Test-password-482!")
        cls.project = Project.objects.create(title="Portfolio", description="My work", tech_stack="Django")

    def project_url(self, action):
        return reverse("main:" + action, args=[self.project.pk])

    def test_public_pages_and_controls(self):
        for user in [None, self.member, self.owner]:
            with self.subTest(user=user):
                if user:
                    self.client.force_login(user)
                response = self.client.get(reverse("main:show_projects"))
                self.assertContains(response, "Portfolio")
                self.assertContains(response, self.project_url("toggle_star"))
                for url in [reverse("main:create_project"), self.project_url("delete_project")]:
                    if user == self.owner:
                        self.assertContains(response, url)
                    else:
                        self.assertNotContains(response, url)
        self.client.logout()
        self.assertEqual(self.client.get(reverse("main:get_projects_json")).status_code, 200)

    def test_anonymous_mutations_redirect_to_login(self):
        from main.models import Project
        for url in [reverse("main:create_project"), self.project_url("delete_project"), self.project_url("toggle_star")]:
            for method in [self.client.get, self.client.post]:
                response = method(url)
                self.assertRedirects(response, reverse("main:login") + "?next=" + url)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_member_cannot_create_or_delete_even_with_forged_cookie(self):
        from main.models import Project
        self.client.force_login(self.member)
        self.client.cookies["last_login"] = "owner"
        for url in [reverse("main:create_project"), self.project_url("delete_project")]:
            for method in [self.client.get, self.client.post]:
                self.assertEqual(method(url, {"title": "Forbidden"}).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

    def test_owner_can_create_and_delete_but_get_does_not_delete(self):
        from main.models import Project
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse("main:create_project")).status_code, 200)
        response = self.client.post(reverse("main:create_project"), {
            "title": "New project", "description": "A new work", "tech_stack": "Python",
        })
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertTrue(Project.objects.filter(title="New project").exists())
        self.client.get(self.project_url("delete_project"))
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())
        self.client.post(self.project_url("delete_project"))
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_star_unstar_are_per_user_and_visible_in_api(self):
        for user in [self.member, self.other, self.owner]:
            self.client.force_login(user)
            self.assertRedirects(self.client.post(self.project_url("toggle_star")), reverse("main:show_projects"))
        self.assertEqual(self.project.starred_by.count(), 3)
        self.assertIn(self.project, self.member.starred_projects.all())
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "Unstar")
        self.assertContains(response, 'class="star-count">3</span>')
        self.assertContains(response, "Dibintangi oleh")
        fields = self.client.get(reverse("main:get_projects_json")).json()[0]["fields"]
        self.assertCountEqual(fields["starred_by"], [["member"], ["other"], ["owner"]])
        self.client.post(self.project_url("toggle_star"))
        self.assertFalse(self.project.starred_by.filter(pk=self.owner.pk).exists())
        self.assertEqual(self.project.starred_by.count(), 2)
        self.assertNotContains(self.client.get(reverse("main:show_projects")), "Unstar")

    def test_get_star_does_not_mutate_and_missing_project_is_404(self):
        import uuid
        self.client.force_login(self.member)
        self.client.get(self.project_url("toggle_star"))
        self.assertEqual(self.project.starred_by.count(), 0)
        self.assertEqual(self.client.post(reverse("main:toggle_star", args=[uuid.uuid4()])).status_code, 404)

    def test_project_search_still_filters_page_and_api(self):
        for page in ["show_projects", "get_projects_json"]:
            self.assertContains(self.client.get(reverse("main:" + page), {"title": "folio"}), "Portfolio")
            response = self.client.get(reverse("main:" + page), {"title": "absent"})
            if page == "get_projects_json":
                self.assertEqual(response.json(), [])
            else:
                self.assertNotContains(response, self.project_url("toggle_star"))

    def test_mutations_require_csrf_and_accept_valid_token(self):
        from django.test import Client
        from main.models import Project
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        for url in [reverse("main:create_project"), self.project_url("delete_project"), self.project_url("toggle_star")]:
            self.assertEqual(client.post(url, {}).status_code, 403)
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())
        self.assertEqual(self.project.starred_by.count(), 0)
        client.get(reverse("main:show_projects"))
        response = client.post(self.project_url("toggle_star"), {
            "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
        })
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertTrue(self.project.starred_by.filter(pk=self.owner.pk).exists())
