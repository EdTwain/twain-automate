from django.urls import path
from . import views
from .views import dashboard_support

urlpatterns = [
    # --- Core Dashboard Pages ---
    path("", views.dashboard_home, name="dashboard_home"),
    path("subscription/", views.dashboard_subscription, name="dashboard_subscription"), 
    path("pricing/", views.pricing_page, name="dashboard_pricing"),
    path("settings/", views.settings_page, name="dashboard_settings"),
    path("support/", dashboard_support, name="dashboard_support"),

    # --- Knowledge Centre ---
    path("knowledge/", views.knowledge_centre_page, name="dashboard_knowledge"),
    path("knowledge/<slug:slug>/", views.knowledge_detail_page, name="dashboard_knowledge_detail"),
    path("knowledge/add/", views.knowledge_add, name="knowledge_add"),
    path("knowledge/<int:pk>/edit/", views.knowledge_edit, name="knowledge_edit"),
    path("knowledge/<int:pk>/delete/", views.knowledge_delete, name="knowledge_delete"),

    # --- Tools ---
    path("tools/", views.tools_page, name="dashboard_tools"),  
    path("tools/add/", views.tool_add, name="tool_add"),
    path("tools/<int:pk>/edit/", views.tool_edit, name="tool_edit"),
    path("tools/<int:pk>/delete/", views.tool_delete, name="tool_delete"),
]
