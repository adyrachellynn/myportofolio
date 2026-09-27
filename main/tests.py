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
        self.assertContains(response, self.edu.title)
        self.assertContains(response, self.edu.institution)
        self.assertContains(response, "Formal Education")

    def test_empty_education_page(self):
        Education.objects.all().delete()
        response = self.client.get(reverse("main:show_education"))
        self.assertContains(response, "Belum ada data pendidikan yang ditambahkan.")


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
