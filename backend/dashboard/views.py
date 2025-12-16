import requests
import base64
import json
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages

from dashboard.models import (
    Message,
    SubscriptionPlan,
    UserSubscription,
    Tool,
    KnowledgeArticle,
    KnowledgeCategory,
)
from admin_dashboard.forms import ToolForm, KnowledgeArticleForm, KnowledgeCategoryForm


# --- Dashboard Home ---
@login_required
def dashboard_home(request):
    # Show welcome message once after signup
    if request.session.get("new_signup"):
        messages.success(request, f"🎉 Account created successfully! Welcome, {request.user.username}.")
        del request.session["new_signup"]

    # Show welcome back message once after login
    elif request.session.get("just_logged_in"):  
        messages.success(request, f"👋 Welcome back, {request.user.username}!")
        del request.session["just_logged_in"]

    # Example overview data – replace with real queries if needed
    overview = {
        "company": "Demo Company Ltd",
        "plan": "Starter",
        "bots_active": 1,
        "integrations": 2,
        "last_activity": "2025-12-15 10:30 AM",
    }
    return render(request, "dashboard/dashboard_home.html", {"overview": overview})


# --- Knowledge Centre ---
@login_required
def knowledge_centre_page(request):
    categories = KnowledgeCategory.objects.filter(is_active=True).order_by("sort_order", "name")
    articles = KnowledgeArticle.objects.filter(is_published=True).order_by("sort_order", "-published_at")
    featured = articles.filter(featured=True)
    return render(request, "dashboard/knowledge_centre.html", {
        "categories": categories,
        "articles": articles,
        "featured": featured,
    })


@login_required
def knowledge_detail_page(request, slug):
    article = KnowledgeArticle.objects.filter(slug=slug, is_published=True).first()
    if not article:
        return render(request, "dashboard/knowledge_not_found.html", status=404)
    return render(request, "dashboard/knowledge_detail.html", {
        "article": article,
        "attachments": article.attachments.all(),
    })


# --- Knowledge CRUD ---
@login_required
def knowledge_add(request):
    if request.method == "POST":
        form = KnowledgeArticleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("dashboard_knowledge")
    else:
        form = KnowledgeArticleForm()
    return render(request, "knowledge/form.html", {"form": form, "action": "Add Article"})


@login_required
def knowledge_edit(request, pk):
    article = get_object_or_404(KnowledgeArticle, pk=pk)
    if request.method == "POST":
        form = KnowledgeArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            return redirect("dashboard_knowledge")
    else:
        form = KnowledgeArticleForm(instance=article)
    return render(request, "knowledge/form.html", {"form": form, "action": "Edit Article"})


@login_required
def knowledge_delete(request, pk):
    article = get_object_or_404(KnowledgeArticle, pk=pk)
    article.delete()
    return redirect("dashboard_knowledge")


# --- Subscription Page ---
@login_required
def dashboard_subscription(request):
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by("sort_order", "price_kes")
    monthly_plans = plans.filter(plan_type="monthly")
    one_time_plans = plans.filter(plan_type="one_time")

    user_sub = None
    if request.user.is_authenticated:
        user_sub = UserSubscription.objects.filter(user=request.user).first()

    return render(request, "dashboard/subscription.html", {
        "monthly_plans": monthly_plans,
        "one_time_plans": one_time_plans,
        "user_sub": user_sub,
    })

# --- Tools Page ---
@login_required
def tools_page(request):
    tools = Tool.objects.filter(is_active=True).order_by("sort_order", "name")
    return render(request, "dashboard/tools.html", {"tools": tools})


# --- Tools CRUD ---
@login_required
def tool_add(request):
    if request.method == "POST":
        form = ToolForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard_tools")
    else:
        form = ToolForm()
    return render(request, "admin_dashboard/tools/form.html", {"form": form, "action": "Add Tool"})


@login_required
def tool_edit(request, pk):
    tool = get_object_or_404(Tool, pk=pk)
    if request.method == "POST":
        form = ToolForm(request.POST, instance=tool)
        if form.is_valid():
            form.save()
            return redirect("dashboard_tools")
    else:
        form = ToolForm(instance=tool)
    return render(request, "admin_dashboard/form.html", {"form": form, "action": "Edit Tool"})


@login_required
def tool_delete(request, pk):
    tool = get_object_or_404(Tool, pk=pk)
    tool.delete()
    return redirect("dashboard_tools")


# --- Support Page ---
@login_required
def dashboard_support(request):
    if request.method == "POST":
        Message.objects.create(
            problem=request.POST.get("problem"),
            urgency=request.POST.get("urgency"),
        )
        return render(request, "dashboard/support.html", {"success": True})
    return render(request, "dashboard/support.html")


# --- Pricing Page ---
@login_required
def pricing_page(request):
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by("sort_order", "price_kes")
    monthly_plans = plans.filter(plan_type="monthly")
    one_time_plans = plans.filter(plan_type="one_time")

    return render(request, "dashboard/pricing.html", {
        "monthly_plans": monthly_plans,
        "one_time_plans": one_time_plans,
    })


# --- Settings Page ---
@login_required
def settings_page(request):
    return render(request, "dashboard/settings.html")



# --- M-Pesa Payment Handlers ---
@login_required
@require_POST
def initiate_payment(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id)
    phone_number = request.POST.get("phone_number", "").strip()

    # Basic validation (expects 2547XXXXXXXX format)
    if not phone_number or not phone_number.startswith("2547") or len(phone_number) != 12:
        return render(request, "dashboard/subscription.html", {
            "monthly_plans": SubscriptionPlan.objects.filter(is_active=True, plan_type="monthly").order_by("sort_order", "price_kes"),
            "one_time_plans": SubscriptionPlan.objects.filter(is_active=True, plan_type="one_time").order_by("sort_order", "price_kes"),
            "user_sub": UserSubscription.objects.filter(user=request.user).first(),
            "payment_error": "Enter a valid phone (2547XXXXXXXX).",
        })
