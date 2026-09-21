from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from main.models import Experience, Education, Project
from main.forms import ProjectForm, EducationForm

def show_main(request):
    context = {
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

def create_project(request):
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
    projects_json = serializers.serialize("json", projects)
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

def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_projects")
    return redirect("main:show_projects")

# --- EDUCATION (INDIVIDUAL ASSIGNMENT 3) ---

def create_education(request):
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

def edit_education(request, education_id):
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
    education_data = Education.objects.all()
    education_json = serializers.serialize("json", education_data)
    return HttpResponse(education_json, content_type="application/json")

def show_education(request):
    json_response = get_education_json(request)
    edu_objects = serializers.deserialize("json", json_response.content.decode("utf-8"))
    education_list = [item.object for item in edu_objects]
    context = {
        "name": "Adyra Rachellyn Arkossand",
        "education_list": education_list,
    }
    return render(request, "education.html", context)

def delete_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)
    if request.method == "POST":
        education.delete()
        messages.success(request, "Education berhasil dihapus!")
        return redirect("main:show_education")
    return redirect("main:show_education")