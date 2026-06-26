from django.shortcuts import render

def login(request):
    return render(request, "login.html")

def register(request):
    return render(request, "register.html")

def home(request):
    return render(request, "home.html")

def eventdetails(request):
    return render(request, "eventdetails.html")

def hosting(request):
    return render(request, "hosting.html")

def about(request):
    return render(request, "about.html")

def support(request):
    return render(request, "support.html")

def careers(request):
    return render(request, "careers.html")

def privacy(request):
    return render(request, "privacy-policy.html")

def terms(request):
    return render(request, "terms-and-conditions.html")

def