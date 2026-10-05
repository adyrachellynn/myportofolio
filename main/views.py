from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from main.models import Experience, Education, Project
from main.forms import ProjectForm, EducationForm
from main.permissions import can_edit_education

def show_main(request):
    context = {
        "last_login": request.COOKIES.get("last_login") or "Belum ada sesi login / Cookie tidak tersedia",
        "name": "Adyra Rachellyn Arkossand",  
        "npm": "2506620620",  
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Sistem Informasi Universitas Indonesia yang berfokus "
            "pada Product Management dan Data Analytics."
        ),
    }
    return render(request, "index.html", context)

def show_experience(request):
    context = {
        "name": "Adyra",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

# --- PROJECTS (TUTORIAL 03) ---

@login_required(login_url="main:login")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")
    context = {
        "name": "Adyra Rachellyn Arkossand",
        "form": form,
    }
    return render(request, "projects_form.html", context)

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    projects_json = serializers.serialize("json", projects, use_natural_foreign_keys=True)
    return HttpResponse(projects_json, content_type="application/json")

def show_projects(request):
    json_response = get_projects_json(request)
    projects = serializers.deserialize("json", json_response.content.decode("utf-8"))
    projects = [project.object for project in projects]
    title_query = request.GET.get("title", "").strip()
    context = {
        "name": "Adyra Rachellyn Arkossand",
        "project_list": projects,
        "title_query": title_query,
    }
    return render(request, "project.html", context)

@login_required(login_url="main:login")
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_projects")
    return redirect("main:show_projects")

# --- EDUCATION (INDIVIDUAL ASSIGNMENT 3) ---

@login_required(login_url="/login/")
def create_education(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = EducationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Education berhasil ditambahkan!")
        return redirect("main:show_education")
    context = {
        "name": "Adyra Rachellyn Arkossand",
        "form": form,
    }
    return render(request, "education_form.html", context)

@require_POST
def create_education_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse({"message": "Hanya superuser yang dapat menambahkan Education."}, status=403)
    form = EducationForm(request.POST)
    if form.is_valid():
        education = form.save()
        return JsonResponse({"message": "Education berhasil ditambahkan.", "pk": str(education.pk)}, status=201)
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@login_required(login_url="/login/")
def edit_education(request, education_id):
    if not can_edit_education(request.user):
        raise PermissionDenied

    education = get_object_or_404(Education, pk=education_id)
    form = EducationForm(request.POST or None, instance=education)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Education berhasil diperbarui!")
        return redirect("main:show_education")
    context = {
        "name": "Adyra Rachellyn Arkossand",
        "form": form,
        "education": education,
    }
    return render(request, "education_form.html", context)

def get_education_json(request):
    title_query = request.GET.get("title", "").strip()
    category_query = request.GET.get("category", "").strip()
    education_data = Education.objects.prefetch_related("starred_by")
    if title_query:
        education_data = education_data.filter(title__icontains=title_query)
    if category_query in dict(Education.CATEGORY_CHOICES):
        education_data = education_data.filter(category=category_query)

    data = []
    for education in education_data:
        starred_users = education.starred_by.all()
        data.append({
            "pk": str(education.pk),
            "fields": {
                "title": education.title,
                "institution": education.institution,
                "year": education.year,
                "category": education.category,
                "category_display": education.get_category_display(),
                "description": education.description,
                "image_url": education.image_url,
                "star_count": len(starred_users),
                "is_starred": request.user in starred_users if request.user.is_authenticated else False,
                "starred_by_names": ", ".join(user.username for user in starred_users),
            },
        })
    return JsonResponse(data, safe=False)

def show_education(request):
    context = {
        "name": "Adyra Rachellyn Arkossand",
        "title_query": request.GET.get("title", "").strip(),
        "can_edit_education": can_edit_education(request.user),
        "form": EducationForm(),
    }
    return render(request, "education.html", context)

@login_required(login_url="/login/")
def delete_education(request, education_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    education = get_object_or_404(Education, pk=education_id)
    if request.method == "POST":
        education.delete()
        messages.success(request, "Education berhasil dihapus!")
        return redirect("main:show_education")
    return redirect("main:show_education")

# --- AUTHENTICATION (TUTORIAL 04) ---

def register(request):
    form = UserCreationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")
    return render(request, "register.html", {
        "name": "Adyra Rachellyn Arkossand", "form": form,
    })


def login_user(request):
    form = AuthenticationForm(
        request, data=request.POST if request.method == "POST" else None,
    )
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        response = redirect("main:show_main")
        response.set_cookie(
            "last_login", timezone.localtime().strftime("%Y-%m-%d %H:%M:%S"),
            httponly=True, samesite="Lax", secure=request.is_secure(),
        )
        return response
    return render(request, "login.html", {
        "name": "Adyra Rachellyn Arkossand", "form": form,
    })


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login", samesite="Lax")
    return response


@login_required(login_url="/login/")
@require_POST
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)
    return redirect("main:show_projects")


@login_required(login_url="/login/")
@require_POST
def toggle_education_star(request, education_id):
    education = get_object_or_404(Education, pk=education_id)
    if education.starred_by.filter(pk=request.user.pk).exists():
        education.starred_by.remove(request.user)
    else:
        education.starred_by.add(request.user)
    return redirect("main:show_education")
