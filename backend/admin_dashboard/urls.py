from django.urls import path
from . import views

urlpatterns = [
    path("", views.admin_dashboard_home, name="admin_dashboard_home"),

    # Messages
    path("messages/", views.admin_messages, name="admin_messages"),
    path("messages/<int:pk>/", views.admin_message_detail, name="admin_message_detail"),
    path("messages/<int:pk>/toggle-read/", views.admin_message_toggle_read, name="admin_message_toggle_read"),
    path("messages/<int:pk>/delete/", views.admin_message_delete, name="admin_message_delete"),

    # Content Manager (existing)
    path("content/", views.content_manager, name="admin_content"),
    path("content/service/<int:id>/edit/", views.edit_service, name="edit_service"),
    path("content/service/<int:id>/delete/", views.delete_service, name="delete_service"),
    path("content/testimonial/<int:id>/edit/", views.edit_testimonial, name="edit_testimonial"),
    path("content/testimonial/<int:id>/delete/", views.delete_testimonial, name="delete_testimonial"),
    path("content/case/<int:id>/edit/", views.edit_case, name="edit_case"),
    path("content/case/<int:id>/delete/", views.delete_case, name="delete_case"),

    # Content Manager (new: Knowledge + Tools)
    path("content/knowledge/", views.admin_knowledge_list, name="admin_knowledge_list"),
    path("content/knowledge/add/", views.admin_knowledge_add, name="admin_knowledge_add"),
    path("content/knowledge/<int:pk>/edit/", views.admin_knowledge_edit, name="admin_knowledge_edit"),
    path("content/knowledge/<int:pk>/delete/", views.admin_knowledge_delete, name="admin_knowledge_delete"),

    path("content/categories/", views.admin_category_list, name="admin_category_list"),
    path("content/categories/add/", views.admin_category_add, name="admin_category_add"),
    path("content/categories/<int:pk>/edit/", views.admin_category_edit, name="admin_category_edit"),
    path("content/categories/<int:pk>/delete/", views.admin_category_delete, name="admin_category_delete"),

    path("content/tools/", views.admin_tool_list, name="admin_tool_list"),
    path("content/tools/add/", views.admin_tool_add, name="admin_tool_add"),
    path("content/tools/<int:pk>/edit/", views.admin_tool_edit, name="admin_tool_edit"),
    path("content/tools/<int:pk>/delete/", views.admin_tool_delete, name="admin_tool_delete"),

    # Other admin sections
    path("analytics/", views.analytics, name="admin_analytics"),
    path("clients/", views.clients, name="admin_clients"),
    path("clients/<int:pk>/activate/", views.admin_client_activate, name="admin_client_activate"),
    path("clients/<int:pk>/cancel/", views.admin_client_cancel, name="admin_client_cancel"),
    path("projects/", views.projects, name="admin_projects"),
    path("notifications/", views.notifications, name="admin_notifications"),
    path("settings/", views.settings, name="admin_settings"),
]
