from django.contrib import admin
from .models import ContactMessage, SubscriptionPlan, SupportMessage, Tool, UserSubscription
from .models import KnowledgeCategory, KnowledgeArticle, KnowledgeAttachment



@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "plan_type",
        "price_kes",
        "badge",          # show badge in admin list
        "highlighted",    # show if plan is highlighted
        "is_active",
        "sort_order",
    )
    list_filter = ("plan_type", "is_active", "highlighted")
    search_fields = ("name", "slug", "description", "features")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "price_kes")  # order plans predictably


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "status",
        "started_at",
        "renewed_at",
        "canceled_at",
    )
    list_filter = ("status", "plan")
    search_fields = ("user__username", "user__email")
    autocomplete_fields = ("user", "plan")  # makes selecting easier




# Knowledge Centre Admins

@admin.register(KnowledgeCategory)
class KnowledgeCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")


class KnowledgeAttachmentInline(admin.TabularInline):
    model = KnowledgeAttachment
    extra = 1
    fields = ("name", "file", "sort_order")


@admin.register(KnowledgeArticle)
class KnowledgeArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "featured", "is_published", "read_time_minutes", "published_at", "updated_at", "sort_order")
    list_filter = ("is_published", "featured", "category")
    search_fields = ("title", "slug", "summary", "content")
    list_editable = ("featured", "is_published", "read_time_minutes", "sort_order")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [KnowledgeAttachmentInline]

    fieldsets = (
        ("Content", {
            "fields": ("title", "slug", "category", "summary", "content")
        }),
        ("Display & Meta", {
            "fields": ("read_time_minutes", "featured", "is_published", "sort_order", "author")
        }),
        ("Media", {
            "fields": ("feature_image", "video_url", "video_file")
        }),
        ("Timestamps", {
            "fields": ("published_at", "updated_at"),
        }),
    )
    readonly_fields = ("published_at", "updated_at")

# Tools We Use 
@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "description")
    ordering = ("sort_order", "name")



@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "business_name", "platform", "description", "created_at", "is_read")
    list_filter = ("platform", "is_read")
    search_fields = ("name", "email", "business_name", "description")
    ordering = ("-created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only show messages that look like contact requests
        return qs.exclude(name="").exclude(email="").exclude(business_name="")


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ("problem", "urgency", "created_at", "is_read")
    list_filter = ("urgency", "is_read")
    search_fields = ("problem",)
    ordering = ("-created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only show messages that look like support tickets
        return qs.exclude(problem="")
