from django import forms
# Import models from the dashboard app
from dashboard.models import KnowledgeCategory, KnowledgeArticle, Tool

class KnowledgeCategoryForm(forms.ModelForm):
    class Meta:
        model = KnowledgeCategory
        fields = ["name", "slug", "description", "sort_order", "is_active"]

class KnowledgeArticleForm(forms.ModelForm):
    class Meta:
        model = KnowledgeArticle
        fields = [
            "title", "slug", "category", "summary", "content",
            "read_time_minutes", "featured", "is_published",
            "feature_image", "video_url", "video_file",
            "sort_order", "author"
        ]

class ToolForm(forms.ModelForm):
    class Meta:
        model = Tool
        fields = ["name", "slug", "description", "icon", "website_url", "sort_order", "is_active"]
