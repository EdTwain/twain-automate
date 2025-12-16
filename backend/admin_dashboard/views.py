from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from dashboard.models import (
    Message, Service, CaseStudy, Client, Project, Testimonial,
    UserSubscription, KnowledgeCategory, KnowledgeArticle, Tool
)
from .forms import KnowledgeCategoryForm, KnowledgeArticleForm, ToolForm


# --- Dashboard Overview ---
@login_required
def admin_dashboard_home(request):
    context = {
        "message_count": Message.objects.count(),
        "unread_count": Message.objects.filter(is_read=False).count(),
        "service_count": Service.objects.count(),
        "case_count": CaseStudy.objects.count(),
        "client_count": Client.objects.count(),
        "recent_projects": Project.objects.order_by('-created_at')[:5],
        "recent_messages": Message.objects.order_by('-created_at')[:5],
    }
    return render(request, "admin_dashboard/index.html", context)


# --- Messages ---
@login_required
def admin_messages(request):
    status = request.GET.get("status")  # 'all', 'read', 'unread'
    qs = Message.objects.all().order_by("-created_at")
    if status == "read":
        qs = qs.filter(is_read=True)
    elif status == "unread":
        qs = qs.filter(is_read=False)

    context = {
        "messages": qs,
        "status": status or "all",
        "message_count": Message.objects.count(),
        "unread_count": Message.objects.filter(is_read=False).count(),
    }
    return render(request, "admin_dashboard/messages/list.html", context)

@login_required
def admin_message_detail(request, pk):
    msg = get_object_or_404(Message, pk=pk)
    if not msg.is_read:
        msg.is_read = True
        msg.save(update_fields=["is_read"])
    return render(request, "admin_dashboard/messages/detail.html", {"msg": msg})

@login_required
@require_POST
def admin_message_toggle_read(request, pk):
    msg = get_object_or_404(Message, pk=pk)
    msg.is_read = not msg.is_read
    msg.save(update_fields=["is_read"])
    return redirect("admin_messages")

@login_required
@require_POST
def admin_message_delete(request, pk):
    msg = get_object_or_404(Message, pk=pk)
    msg.delete()
    return redirect("admin_messages")


# --- Analytics ---
def analytics(request):
    return render(request, "admin_dashboard/analytics.html")


# --- Clients ---
@login_required
def clients(request):
    subscriptions = UserSubscription.objects.select_related("user", "plan").order_by("-started_at")
    return render(request, "admin_dashboard/clients.html", {"subscriptions": subscriptions})

@require_POST
def admin_client_activate(request, pk):
    sub = get_object_or_404(UserSubscription, pk=pk)
    sub.status = "active"
    sub.started_at = sub.started_at or timezone.now()
    sub.save()
    return redirect("admin_clients")

@require_POST
def admin_client_cancel(request, pk):
    sub = get_object_or_404(UserSubscription, pk=pk)
    sub.status = "canceled"
    sub.canceled_at = timezone.now()
    sub.save()
    return redirect("admin_clients")


# --- Content Manager Overview ---
@login_required
def content_manager(request):
    context = {
        "services": Service.objects.all(),
        "case_studies": CaseStudy.objects.all(),
        "testimonials": Testimonial.objects.all(),
        "categories": KnowledgeCategory.objects.all(),
        "articles": KnowledgeArticle.objects.select_related("category"),
        "tools": Tool.objects.all(),
    }
    return render(request, "admin_dashboard/content.html", context)


# --- Services ---
@login_required
def edit_service(request, id):
    service = get_object_or_404(Service, id=id)
    if request.method == "POST":
        service.title = request.POST.get("title", service.title)
        service.description = request.POST.get("description", service.description)
        service.save()
        return redirect("admin_content")
    return render(request, "admin_dashboard/edit_service.html", {"service": service})

@login_required
def delete_service(request, id):
    get_object_or_404(Service, id=id).delete()
    return redirect("admin_content")


# --- Testimonials ---
@login_required
def edit_testimonial(request, id):
    testimonial = get_object_or_404(Testimonial, id=id)
    if request.method == "POST":
        testimonial.client_name = request.POST.get("client_name", testimonial.client_name)
        testimonial.feedback = request.POST.get("feedback", testimonial.feedback)
        testimonial.save()
        return redirect("admin_content")
    return render(request, "admin_dashboard/edit_testimonial.html", {"testimonial": testimonial})

@login_required
def delete_testimonial(request, id):
    get_object_or_404(Testimonial, id=id).delete()
    return redirect("admin_content")


# --- Case Studies ---
@login_required
def edit_case(request, id):
    case = get_object_or_404(CaseStudy, id=id)
    if request.method == "POST":
        case.project_name = request.POST.get("project_name", case.project_name)
        case.outcome = request.POST.get("outcome", case.outcome)
        case.save()
        return redirect("admin_content")
    return render(request, "admin_dashboard/edit_case.html", {"case": case})

@login_required
def delete_case(request, id):
    get_object_or_404(CaseStudy, id=id).delete()
    return redirect("admin_content")


# --- Knowledge Categories ---
@login_required
def admin_category_list(request):
    categories = KnowledgeCategory.objects.all()
    return render(request, "admin_dashboard/categories/list.html", {"categories": categories})

@login_required
def admin_category_add(request):
    form = KnowledgeCategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("admin_category_list")
    return render(request, "admin_dashboard/categories/form.html", {"form": form})

@login_required
def admin_category_edit(request, pk):
    category = get_object_or_404(KnowledgeCategory, pk=pk)
    form = KnowledgeCategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("admin_category_list")
    return render(request, "admin_dashboard/categories/form.html", {"form": form})

@login_required
@require_POST
def admin_category_delete(request, pk):
    get_object_or_404(KnowledgeCategory, pk=pk).delete()
    return redirect("admin_category_list")


# --- Knowledge Articles ---
@login_required
def admin_knowledge_list(request):
    articles = KnowledgeArticle.objects.select_related("category").order_by("-published_at")
    return render(request, "admin_dashboard/knowledge/list.html", {"articles": articles})

@login_required
def admin_knowledge_add(request):
    form = KnowledgeArticleForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("admin_knowledge_list")
    return render(request, "admin_dashboard/knowledge/form.html", {"form": form})

@login_required
def admin_knowledge_edit(request, pk):
    article = get_object_or_404(KnowledgeArticle, pk=pk)
    form = KnowledgeArticleForm(request.POST or None, request.FILES or None, instance=article)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("admin_knowledge_list")
    return render(request, "admin_dashboard/knowledge/form.html", {"form": form})

@login_required
@require_POST
def admin_knowledge_delete(request, pk):
    get_object_or_404(KnowledgeArticle, pk=pk).delete()
    return redirect("admin_knowledge_list")


# --- Tools ---
@login_required
def admin_tool_list(request):
    tools = Tool.objects.all()
    return render(request, "admin_dashboard/tools/list.html", {"tools": tools})

@login_required
def admin_tool_add(request):
    form = ToolForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("admin_tool_list")
    return render(request, "admin_dashboard/tools/form.html", {"form": form})

@login_required
def admin_tool_edit(request, pk):
    tool = get_object_or_404(Tool, pk=pk)
    form = ToolForm(request.POST or None, instance=tool)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("admin_tool_list")
    return render(request, "admin_dashboard/tools/form.html", {"form": form})

@login_required
@require_POST
def admin_tool_delete(request, pk):
    get_object_or_404(Tool, pk=pk).delete()
    return redirect("admin_tool_list")


# --- Projects ---
def projects(request):
    projects = Project.objects.order_by('-created_at')
    return render(request, "admin_dashboard/projects.html", {"projects": projects})


# --- Notifications ---
def notifications(request):
    return render(request, "admin_dashboard/notifications.html")


# --- Settings ---
def settings(request):
    return render(request, "admin_dashboard/settings.html")
