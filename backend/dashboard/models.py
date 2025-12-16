from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()

# Subscription Models
class SubscriptionPlan(models.Model):
    PLAN_TYPE_CHOICES = [
        ("monthly", "Monthly Subscription"),
        ("one_time", "One-Time Setup"),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default="monthly")
    price_kes = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    features = models.TextField(blank=True, help_text="Comma-separated list of features")
    badge = models.CharField(max_length=50, blank=True, help_text="Optional badge like 'Most Popular'")
    highlighted = models.BooleanField(default=False, help_text="If True, visually emphasize this plan")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    def feature_list(self):
        return [f.strip() for f in self.features.split(",")] if self.features else []

    def __str__(self):
        return f"{self.name} ({self.get_plan_type_display()})"

class UserSubscription(models.Model):
    STATUS_CHOICES = [
        ("inactive", "Inactive"),
        ("active", "Active"),
        ("past_due", "Past Due"),
        ("canceled", "Canceled"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="subscription")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="inactive")
    started_at = models.DateTimeField(null=True, blank=True)
    renewed_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} – {self.plan or 'No plan'} ({self.status})"

    # Helper methods
    def activate(self, plan: SubscriptionPlan):
        """Activate subscription when payment succeeds."""
        from django.utils import timezone
        self.plan = plan
        self.status = "active"
        if not self.started_at:
            self.started_at = timezone.now()
        self.renewed_at = timezone.now()
        self.save()

    def cancel(self):
        """Cancel subscription manually."""
        from django.utils import timezone
        self.status = "canceled"
        self.canceled_at = timezone.now()
        self.save()



# Knowledge Centre Models

class KnowledgeCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

class KnowledgeArticle(models.Model):
    # Core
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    category = models.ForeignKey(KnowledgeCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="articles")
    summary = models.TextField(blank=True, help_text="Short intro shown in cards.")
    content = models.TextField(help_text="Full documentation body (Markdown or HTML).")

    # Display and metadata
    read_time_minutes = models.PositiveIntegerField(default=5, help_text="Estimated read time (minutes).")
    featured = models.BooleanField(default=False, help_text="If True, can be highlighted in the list.")
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    # Media
    feature_image = models.ImageField(upload_to="knowledge/images/", blank=True, null=True)
    video_url = models.URLField(blank=True, help_text="Optional link to YouTube/Vimeo/etc.")
    video_file = models.FileField(upload_to="knowledge/videos/", blank=True, null=True, help_text="Optional uploaded video file.")

    # Audit
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="knowledge_articles")
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("dashboard_knowledge_detail", kwargs={"slug": self.slug})

    def video_embed_url(self):
        """
        Returns a safe YouTube/Vimeo embed URL from a typical share/watch URL.
        """
        if not self.video_url:
            return ""
        url = self.video_url.strip()

        # YouTube watch/share -> embed
        if "youtube.com/watch" in url:
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(url).query)
            vid = qs.get("v", [""])[0]
            return f"https://www.youtube.com/embed/{vid}"
        if "youtu.be/" in url:
            vid = url.split("youtu.be/")[-1].split("?")[0]
            return f"https://www.youtube.com/embed/{vid}"

        # Vimeo basic handling
        if "vimeo.com/" in url:
            vid = url.rstrip("/").split("/")[-1]
            return f"https://player.vimeo.com/video/{vid}"

        return url

class KnowledgeAttachment(models.Model):
    article = models.ForeignKey(KnowledgeArticle, on_delete=models.CASCADE, related_name="attachments")
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to="knowledge/attachments/")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.article.title} – {self.name}"


# Tools Model
class Tool(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True, help_text="Short description of the tool")
    icon = models.CharField(max_length=50, blank=True, help_text="Optional icon class (e.g. Bootstrap or FontAwesome)")
    website_url = models.URLField(blank=True, help_text="Official website or documentation link")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

class Message(models.Model):
    # Website contact fields
    name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    business_name = models.CharField(max_length=200, blank=True)
    platform = models.CharField(max_length=50, blank=True)  # WhatsApp, Instagram, etc.
    description = models.TextField(blank=True)  # "Tell us what you'd like your bot to do"

    # Dashboard support fields
    problem = models.TextField(blank=True)
    urgency = models.CharField(
        max_length=20,
        choices=[("Low", "General Inquiry"), ("Medium", "Issue affecting workflow"), ("High", "Critical")],
        blank=True,
    )

    # Common fields
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name or 'Anonymous'} — {self.email or 'No email'}"



class Service(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    client_name = models.CharField(max_length=100)
    feedback = models.TextField()

    def __str__(self):
        return self.client_name


class CaseStudy(models.Model):
    project_name = models.CharField(max_length=150)
    outcome = models.TextField()

    def __str__(self):
        return self.project_name

class Client(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Proxy models to separate Contact Requests and Support Tickets in admin
class ContactMessage(Message):
    class Meta:
        proxy = True
        verbose_name = "Contact Request"
        verbose_name_plural = "Contact Requests"


class SupportMessage(Message):
    class Meta:
        proxy = True
        verbose_name = "Support Ticket"
        verbose_name_plural = "Support Tickets"
        

