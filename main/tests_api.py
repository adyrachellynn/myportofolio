import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Education, Project


class EducationAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.regular = User.objects.create_user('api-regular', password='Test-password-482!')
        cls.editor = User.objects.create_user('api-editor')
        cls.editor.groups.add(Group.objects.create(name='Editor'))
        cls.owner = User.objects.create_superuser('api-owner', 'owner@example.com', 'Test-password-482!')
        cls.education = Education.objects.create(
            title='Degree', institution='UI', year='2026', category='formal', description='Original description',
        )

    def setUp(self):
        self.list_url = reverse('api:education-list')
        self.detail_url = reverse('api:education-detail', args=[self.education.pk])
        self.star_url = reverse('api:education-star', args=[self.education.pk])
        self.payload = {'title': 'New Education', 'institution': 'UI', 'year': '2026', 'category': 'cert'}

    def test_public_list_has_flat_public_fields(self):
        self.education.starred_by.add(self.regular)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        row = response.json()[0]
        self.assertEqual(set(row), {'id', 'title', 'institution', 'year', 'category', 'category_display',
                                    'description', 'image_url', 'star_count', 'is_starred', 'starred_by_names'})
        self.assertEqual(row['id'], str(self.education.pk))
        self.assertFalse(row['is_starred'])
        self.assertEqual(row['star_count'], 1)
        self.assertEqual(row['category_display'], 'Formal Education')
        self.assertNotIn('pk', row)
        self.assertNotIn('fields', row)

    def test_public_detail_and_missing_uuid(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], str(self.education.pk))
        self.assertEqual(self.client.get(reverse('api:education-detail', args=[uuid.uuid4()])).status_code, 404)

    def test_title_category_and_combined_filters(self):
        cert = Education.objects.create(**{**self.payload, 'title': 'Degree Certificate'})
        course = Education.objects.create(**{**self.payload, 'title': 'Python', 'category': 'course'})
        cases = [({'title': ' dEgReE '}, [self.education, cert]),
                 ({'category': 'formal'}, [self.education]), ({'category': 'cert'}, [cert]),
                 ({'category': 'course'}, [course]),
                 ({'title': 'degree', 'category': ' cert '}, [cert]),
                 ({'title': 'degree', 'category': 'course'}, []),
                 ({'title': 'absent'}, []),
                 ({'category': ''}, [self.education, cert, course]),
                 ({'category': 'invalid'}, [self.education, cert, course])]
        for params, expected in cases:
            with self.subTest(params=params):
                response = self.client.get(self.list_url, params)
                self.assertEqual(response.status_code, 200)
                self.assertCountEqual([row['id'] for row in response.data], [str(item.pk) for item in expected])

    def test_only_superuser_can_create(self):
        for user in [None, self.regular, self.editor]:
            with self.subTest(user=user):
                self.client.force_authenticate(user=user)
                self.assertEqual(self.client.post(self.list_url, self.payload, format='json').status_code, 403)
        self.assertEqual(Education.objects.count(), 1)
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Education.objects.get(pk=response.data['id']).title, self.payload['title'])

    def test_invalid_post_does_not_save(self):
        self.client.force_authenticate(user=self.owner)
        for field, value in [('title', ' '), ('title', '<img src="x" onerror="alert(1)">'),
                             ('category', 'invalid'), ('image_url', 'javascript:alert(1)'),
                             ('institution', ''), ('year', '')]:
            with self.subTest(field=field, value=value):
                response = self.client.post(self.list_url, {**self.payload, field: value}, format='json')
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
        self.assertEqual(Education.objects.count(), 1)

    def test_only_editor_and_superuser_can_update(self):
        for user in [None, self.regular]:
            self.client.force_authenticate(user=user)
            for method in [self.client.patch, self.client.put]:
                self.assertEqual(method(self.detail_url, self.payload, format='json').status_code, 403)
        self.education.refresh_from_db()
        self.assertEqual(self.education.title, 'Degree')
        for user in [self.editor, self.owner]:
            self.client.force_authenticate(user=user)
            for method in [self.client.patch, self.client.put]:
                response = method(self.detail_url, self.payload, format='json')
                self.assertEqual(response.status_code, 200)
                self.education.refresh_from_db()
                self.assertEqual(self.education.title, self.payload['title'])

    def test_patch_preserves_omitted_fields_and_put_requires_fields(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {'title': 'Changed'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.education.refresh_from_db()
        self.assertEqual(self.education.description, 'Original description')
        self.assertEqual(self.education.institution, 'UI')
        self.assertEqual(self.education.year, '2026')
        response = self.client.put(self.detail_url, {'title': 'Incomplete'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('institution', response.data)
        self.assertIn('year', response.data)
        self.education.refresh_from_db()
        self.assertEqual(self.education.title, 'Changed')

    def test_only_superuser_can_delete_with_empty_response(self):
        for user in [None, self.regular, self.editor]:
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
            self.assertTrue(Education.objects.filter(pk=self.education.pk).exists())
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b'')
        self.assertFalse(Education.objects.filter(pk=self.education.pk).exists())
        self.assertEqual(self.client.get(self.detail_url).status_code, 404)

    def test_star_requires_login_and_uses_current_user(self):
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.assertEqual(self.education.starred_by.count(), 0)
        for user in [self.regular, self.editor, self.owner]:
            self.client.force_authenticate(user=user)
            response = self.client.post(self.star_url, {'user_id': self.owner.pk}, format='json')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.data['is_starred'])
            self.assertEqual(response.data['star_count'], 1)
            self.assertEqual(response.data['starred_by_names'], user.username)
            self.assertEqual(list(self.education.starred_by.all()), [user])
            response = self.client.post(self.star_url)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.data['is_starred'])
            self.assertEqual(response.data['star_count'], 0)

    def test_star_status_and_counts_are_per_user(self):
        for count, user in enumerate([self.regular, self.editor, self.owner], start=1):
            self.client.force_authenticate(user=user)
            response = self.client.post(self.star_url)
            self.assertTrue(response.data['is_starred'])
            self.assertEqual(response.data['star_count'], count)
        self.client.post(self.star_url)
        self.client.force_authenticate(user=self.regular)
        response = self.client.get(self.detail_url)
        self.assertTrue(response.data['is_starred'])
        self.assertEqual(response.data['star_count'], 2)
        self.client.force_authenticate(user=None)
        self.assertFalse(self.client.get(self.detail_url).data['is_starred'])

    def test_safe_and_unsupported_methods(self):
        for url in [self.list_url, self.detail_url]:
            for method in [self.client.head, self.client.options]:
                self.assertEqual(method(url).status_code, 200)
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.get(self.star_url).status_code, 405)
        self.assertEqual(self.client.delete(self.list_url).status_code, 405)
        self.assertEqual(self.client.post(self.detail_url, self.payload, format='json').status_code, 405)
        self.assertEqual(Education.objects.count(), 1)
        self.assertEqual(self.education.starred_by.count(), 0)

    def test_read_only_and_excluded_fields_cannot_be_forged(self):
        self.client.force_authenticate(user=self.owner)
        forged_id = uuid.uuid4()
        forged = {'id': str(forged_id), 'category_display': 'Forged', 'star_count': 99,
                  'is_starred': True, 'starred_by_names': 'Forged', 'starred_by': [self.regular.pk]}
        response = self.client.post(self.list_url, {**self.payload, **forged}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.data['id'], str(forged_id))
        created_id = response.data['id']
        self.education.starred_by.add(self.regular)
        for method in [self.client.patch, self.client.put]:
            response = method(self.detail_url, {**self.payload, **forged}, format='json')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['id'], str(self.education.pk))
            self.assertEqual(response.data['category_display'], 'Certification')
            self.assertEqual(response.data['star_count'], 1)
            self.assertFalse(response.data['is_starred'])
            self.assertEqual(response.data['starred_by_names'], self.regular.username)
        created = Education.objects.get(pk=created_id)
        self.assertEqual(created.starred_by.count(), 0)
        self.education.refresh_from_db()
        self.assertEqual(list(self.education.starred_by.all()), [self.regular])
        self.assertFalse(Education.objects.filter(pk=forged_id).exists())

    def test_session_post_requires_csrf_and_valid_role(self):
        for user in [self.owner, self.regular]:
            client = APIClient(enforce_csrf_checks=True)
            self.assertTrue(client.login(username=user.username, password='Test-password-482!'))
            before = Education.objects.count()
            self.assertEqual(client.post(self.list_url, self.payload, format='json').status_code, 403)
            self.assertEqual(Education.objects.count(), before)
            self.assertEqual(client.get(reverse('main:show_education')).status_code, 200)
            response = client.post(self.list_url, self.payload, format='json',
                                   HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)
            self.assertEqual(response.status_code, 201 if user == self.owner else 403)
            self.assertEqual(Education.objects.count(), before + (1 if user == self.owner else 0))

class ProjectAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.regular = User.objects.create_user(
            "project-regular",
            password="Test-password-482!",
        )
        editor_group, _ = Group.objects.get_or_create(name="Editor")
        cls.editor = User.objects.create_user(
            "project-editor",
            password="Test-password-482!",
        )
        cls.editor.groups.add(editor_group)

        cls.owner = User.objects.create_superuser(
            "project-owner",
            "project-owner@example.com",
            "Test-password-482!",
        )
        cls.project = Project.objects.create(
            title="Portfolio Website",
            description="Personal portfolio project",
            tech_stack="Django, JavaScript",
        )

    def setUp(self):
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse(
            "api:project-detail",
            args=[self.project.pk],
        )
        self.star_url = reverse(
            "api:project-star",
            args=[self.project.pk],
        )
        self.payload = {
            "title": "New Project",
            "description": "New project description",
            "tech_stack": "Django",
            "project_url": "",
            "project_image_url": "",
        }

    def test_public_list_and_title_search(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], str(self.project.pk))
        self.assertEqual(response.data[0]["title"], self.project.title)
        self.assertFalse(response.data[0]["is_starred"])
        self.assertEqual(response.data[0]["star_count"], 0)
        self.assertNotIn("password", response.data[0])

        response = self.client.get(self.list_url, {"title": " PORTFOLIO "})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(self.list_url, {"title": "tidak ada"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_public_detail_and_missing_project(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(self.project.pk))

        missing_url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(missing_url).status_code, 404)

    def test_guest_regular_and_editor_cannot_create(self):
        for user in [None, self.regular, self.editor]:
            with self.subTest(user=user):
                self.client.force_authenticate(user=user)
                before = Project.objects.count()

                response = self.client.post(
                    self.list_url,
                    self.payload,
                    format="json",
                )

                self.assertEqual(response.status_code, 403)
                self.assertEqual(Project.objects.count(), before)

    def test_superuser_can_create_project(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.list_url,
            self.payload,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(response.data["title"], "New Project")

    def test_invalid_project_does_not_save(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.list_url,
            {**self.payload, "title": "<img src=x onerror=alert(1)>"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_guest_and_regular_cannot_update(self):
        for user in [None, self.regular]:
            with self.subTest(user=user):
                self.client.force_authenticate(user=user)

                response = self.client.patch(
                    self.detail_url,
                    {"title": "Tidak Boleh Berubah"},
                    format="json",
                )

                self.assertEqual(response.status_code, 403)
                self.project.refresh_from_db()
                self.assertEqual(self.project.title, "Portfolio Website")

    def test_editor_and_superuser_can_update(self):
        self.client.force_authenticate(user=self.editor)

        response = self.client.patch(
            self.detail_url,
            {"title": "Diubah Editor"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Diubah Editor")
        self.assertEqual(
            self.project.description,
            "Personal portfolio project",
        )

        self.client.force_authenticate(user=self.owner)

        response = self.client.put(
            self.detail_url,
            {
                **self.payload,
                "title": "Diubah Superuser",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Diubah Superuser")

    def test_only_superuser_can_delete(self):
        for user in [None, self.regular, self.editor]:
            with self.subTest(user=user):
                self.client.force_authenticate(user=user)

                response = self.client.delete(self.detail_url)

                self.assertEqual(response.status_code, 403)
                self.assertTrue(
                    Project.objects.filter(pk=self.project.pk).exists()
                )

        self.client.force_authenticate(user=self.owner)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(
            Project.objects.filter(pk=self.project.pk).exists()
        )

    def test_star_requires_login_and_uses_current_user(self):
        response = self.client.post(self.star_url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.project.starred_by.count(), 0)

        self.client.force_authenticate(user=self.regular)

        response = self.client.post(self.star_url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(
            response.data["starred_by_names"],
            self.regular.username,
        )

        response = self.client.post(self.star_url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_session_post_requires_csrf(self):
        client = APIClient(enforce_csrf_checks=True)

        self.assertTrue(
            client.login(
                username=self.owner.username,
                password="Test-password-482!",
            )
        )

        response = client.post(
            self.list_url,
            self.payload,
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

        client.get(reverse("main:show_projects"))

        response = client.post(
            self.list_url,
            self.payload,
            format="json",
            HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Project.objects.count(), 2)