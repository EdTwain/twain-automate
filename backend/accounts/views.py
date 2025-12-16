from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # ✅ Only set login flag here
            request.session["just_logged_in"] = True
            return redirect("dashboard_home")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("homepage")

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("homepage")   # redirect to core/index.html


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, "accounts/signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return render(request, "accounts/signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, "accounts/signup.html")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        # ✅ Only set signup flag here
        request.session["new_signup"] = True

        return redirect("dashboard_home")

    return render(request, "accounts/signup.html")
