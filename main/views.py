from django.shortcuts import render

from main.models import Experience

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
        "name": "Adyra",  # Pastikan sama dengan nama di show_main
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)