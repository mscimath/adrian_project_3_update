from django.contrib import admin
from .models import Service
from .models import Reservation
from .models import BlogPost, BlogCategory

admin.site.register(Service)
admin.site.register(Reservation)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "created_at")
    list_filter = ("is_published", "category", "created_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "content")
    date_hierarchy = "created_at"

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}