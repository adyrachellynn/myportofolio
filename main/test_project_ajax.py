from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse

from main.forms import ProjectForm
from main.models import Project


class ProjectAjaxTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = User.objects.create_user("ajax-reader")
        cls.editor = User.objects.create_user("ajax-editor")
        cls.editor.groups.add(Group.objects.create(name="Editor"))
        cls.owner = User.objects.create_superuser(
            "ajax-owner",
            "owner@example.com",
            "Test-password-482!",
        )

    def setUp(self):
        self.url = reverse("main:create_project_ajax")
        self.payload = {
            "title": "Portfolio",
            "description": "My work",
            "tech_stack": "Django",
        }

    def test_post_only_and_superuser_create(self):
        for user in [None, self.member, self.editor, self.owner]:
            self.client.logout()

            if user:
                self.client.force_login(user)

            self.assertEqual(self.client.get(self.url).status_code, 405)

            response = self.client.post(self.url, self.payload)
            self.assertEqual(response.status_code, 201 if user == self.owner else 403)

            if user == self.owner:
                self.assertTrue(
                    Project.objects.filter(pk=response.json()["pk"]).exists()
                )

        self.assertEqual(Project.objects.count(), 1)

    def test_invalid_and_tag_only_input_not_saved(self):
        self.client.force_login(self.owner)

        for field, value in [
            ("title", " "),
            ("title", "<img src=x onerror=alert(1)>"),
            ("project_url", "javascript:alert(1)"),
            ("project_image_url", "javascript:alert(1)"),
        ]:
            response = self.client.post(self.url, {**self.payload, field: value})

            self.assertEqual(response.status_code, 400)
            self.assertIn(field, response.json()["errors"])

        self.assertEqual(Project.objects.count(), 0)

    def test_text_cleaning_and_legacy_form_share_validation(self):
        form = ProjectForm(
            {
                **self.payload,
                "title": " <b>Portfolio</b> ",
                "description": "<p>My work</p>",
                "tech_stack": "<b>Django</b>",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)

        for field, value in self.payload.items():
            self.assertEqual(form.cleaned_data[field], value)

        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("main:create_project"),
            {**self.payload, "title": "<img src=x>"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.context["form"].errors)
        self.assertEqual(Project.objects.count(), 0)

    def test_csrf_and_modal_guest_safety(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)

        self.assertEqual(client.post(self.url, self.payload).status_code, 403)

        page = client.get(reverse("main:show_projects"))

        self.assertContains(page, 'id="project-form"')
        self.assertContains(page, 'id="add-project-modal"')

        self.assertEqual(
            client.post(
                self.url,
                self.payload,
                HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
            ).status_code,
            201,
        )

        self.client.logout()
        page = self.client.get(reverse("main:show_projects"))

        self.assertNotContains(page, 'id="project-form"')
        self.assertContains(page, "if (projectForm)")

    def test_json_search_and_legacy_contract(self):
        project = Project.objects.create(**self.payload)
        project.starred_by.add(self.member)

        url = reverse("main:get_projects_json")
        data = self.client.get(url, {"title": "  fOLIo  "}).json()

        self.assertEqual(data[0]["pk"], str(project.pk))
        self.assertEqual(data[0]["fields"]["star_count"], 1)
        self.assertFalse(data[0]["fields"]["is_starred"])

        self.client.force_login(self.member)
        fields = self.client.get(url).json()[0]["fields"]

        self.assertTrue(fields["is_starred"])
        self.assertEqual(fields["starred_by_names"], self.member.username)
        self.assertNotIn("password", fields)
        self.assertEqual(self.client.get(url, {"title": "absent"}).json(), [])

    def test_old_untrusted_text_is_not_server_rendered(self):
        payload = "<img src=x onerror=alert(1)>"
        Project.objects.create(**{**self.payload, "title": payload})

        page = self.client.get(reverse("main:show_projects"))

        self.assertNotContains(page, payload)
        self.assertContains(page, "${escapeHtml(project.title)}")
        self.assertContains(page, "${escapeHtml(project.project_image_url)}")
        self.assertContains(page, "${escapeHtml(project.starred_by_names)}")

        # Frontend Tutorial 07 memang menggunakan endpoint DRF.
        self.assertContains(page, "/api/v1/projects/")

        self.assertEqual(
            self.client.get(reverse("main:get_projects_json")).json()[0]["fields"]["title"],
            payload,
        )