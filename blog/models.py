from django.db import models
from django.urls import reverse
from accounts.models import CustomUser
from core.models import Disease
from .managers import PostManager
from tinymce.models import HTMLField
from django.conf import settings
from django.utils import timezone
from django.db.models import Count


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    content = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    categories = models.ManyToManyField(Category, related_name='posts')
    tags = models.ManyToManyField(Tag, related_name='posts')
    related_diseases = models.ManyToManyField(Disease, blank=True, related_name='posts')
    image = models.ImageField(upload_to='uploads/blog_images/', null=True, blank=True)

    objects = PostManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('', kwargs={'pk': self.id})


class Feed(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = HTMLField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='feeds', null=True, blank=True)
    video = models.FileField(upload_to='uploads/feeds', blank=True, null=True)
    posts = models.ManyToManyField(Post, related_name='feeds')
    diseases = models.ManyToManyField(Disease, related_name='feeds')
    categories = models.ManyToManyField(Category, related_name='feeds')
    tags = models.ManyToManyField(Tag, related_name='feeds')
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    author_name = models.CharField(max_length=100, blank=True, null=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)  # Optional
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f"Comment by {self.author_name or self.author.email} on {self.post.title}"

