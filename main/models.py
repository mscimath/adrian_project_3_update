from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse


class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file_path = models.CharField(max_length=500)
    time = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title


class SubService(models.Model):
    service = models.ForeignKey(
        Service,
        related_name='subservice',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)
    photo = models.URLField(blank=True)
    duration = models.IntegerField(help_text="Time Duration in hours")

    def __str__(self):
        return f"{self.title} ({self.service.title})"


class Reservation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reservations',
        default=1
    )
    service = models.ForeignKey(
        'Service',           # nazwa modelu usług
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"{self.service.name} - {self.date} {self.time}"


class Review(models.Model):
    name = models.CharField(max_length=100)  # Imię autora opinii
    email = models.EmailField(blank=True, null=True)  # opcjonalnie
    content = models.TextField()  # Treść opinii
    rating = models.PositiveSmallIntegerField(default=5)  # Ocena 1-5
    created_at = models.DateTimeField(auto_now_add=True)  # Data dodania

    def __str__(self):
        return f"{self.name} - {self.rating}"

class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    excerpt = models.TextField(
        blank=True, 
        help_text="Short preview text"
    )
    
    content = models.TextField(
        help_text="Main blog content"
    )
    
    #need to install pillow before using it
    #featured_image = models.ImageField(
    #    upload_to="blog/",
    #    blank=True,
    #    null=True
    #)
    
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"] # Most recent first

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog_detail", kwargs={"slug": self.slug})
    
    # For categorizing blog posts
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts"
    )
    
class BlogSection(models.Model):
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name="sections"
    )
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    content = models.TextField()

    class Meta: 
        ordering = ["order"]

    def __str__(self):
        return f"{self.post.title} - {self.title}"
    
