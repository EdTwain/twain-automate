from django.shortcuts import render, redirect
from dashboard.models import Message
from django.contrib import messages

def index(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        business_name = request.POST.get("business_name")
        platform = request.POST.get("platform")
        description = request.POST.get("description")

        # Save message to database
        Message.objects.create(
            name=name,
            email=email,
            business_name=business_name,
            platform=platform,
            description=description,
        )

        # Add a success flash message
        messages.success(request, "✅ Your request has been submitted successfully!")

        # Redirect to homepage (avoid resubmission on refresh)
        return redirect("homepage")

    # GET request → just render homepage
    return render(request, "core/index.html")
