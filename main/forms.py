from django.forms import ModelForm, TextInput, Textarea, URLInput, Select
from main.models import Project, Education

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
            

        ]

        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "tech_stack": "Teknologi yang Digunakan",
            "project_url": "URL Proyek",
            "project_image_url": "URL Gambar Proyek",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Proyekmu",
                    "rows": 3,
                }
            ),
            "tech_stack": TextInput(
                attrs={
                    "placeholder": "Django, Python, HTML, CSS",
                }
            ),
            "project_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/kakBurhan/burhanquestv4",
                }
            ),
            "project_image_url": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
        }

class EducationForm(ModelForm):
    class Meta:
        model = Education
        fields = [
            "title",
            "institution",
            "year",
            "category",
            "description",
            "image_url",

        ]

        labels = {
            "title": "Nama Gelar / Sertifikasi",
            "institution": "Institusi / Penyelenggara",
            "year": "Tahun / Periode",
            "category": "Kategori",
            "description": "Deskripsi",
            "image_url": "URL Gambar / Logo Institusi",

        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "S1 Sistem Informasi",
                    "maxlength": 255,
                }
            ),
            "institution": TextInput(
                attrs={
                    "placeholder": "Universitas Indonesia",
                    "maxlength": 255,
                }
            ),
            "year": TextInput(
                attrs={
                    "placeholder": "2025 - Sekarang",
                    "maxlength": 50,
                }
            ),
            "category": Select(),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan fokus studi, topik riset, atau pencapaianmu...",
                    "rows": 3,
                }
            ),
            "image_url": URLInput(
                attrs={"placeholder": "https://... (URL gambar logo atau foto kampus)"}
            ),
        }