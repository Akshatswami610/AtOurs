from django.shortcuts import render

def login(request):
    return render(request, "login.html")

def register(request):
    return render(request, "register.html")

def resetpassword(request):
    return render(request, "reset-password.html")

def home(request):
    return render(request, "home.html")

def me(request):
    return render(request, "me.html")

def events(request):
    return render(request, "events.html")

def earning(request):
    return render(request, "earning.html")

def eventdetails(request, id):
    return render(request, "event-details.html")

def bookingcheckout(request):
    return render(request, "booking-checkout.html")

def hosting(request):
    return render(request, "hosting.html")

def profile(request):
    return render(request, "profile.html")

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

def team(request):
    return render(request, "team.html")

def mytickets(request):
    return render(request, "my-tickets.html")
