from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.db.models import Q, Count
from .models import Post, Category, Tag, Comment, Feed
from .forms import CommentForm
from accounts.models import CustomUser, DoctorProfile
from core.models import Disease, DiseaseSymptom
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect


class IndexView(TemplateView):
    template_name = 'blog/index.html'


class PostListView(ListView):
    model = Post
    template_name = 'blog/articles/blogs.html'
    context_object_name = 'posts'
    queryset = Post.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Annotate the count of posts for each tag
        context['tags'] = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        # Annotate the count of posts for each category
        context['categories'] = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        # Annotate the count of posts for each doctor (CustomUser)
        context['doctors'] = CustomUser.objects.filter(role='doctor').annotate(post_count=Count('posts')).order_by(
            '-post_count')
        # Annotate the count of posts for each disease
        context['diseases'] = Disease.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        context['featured_posts'] = Post.objects.filter(published=True, featured=True).order_by('-created_at')[:3]
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/articles/post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        # Fetch the current post's categories and tags safely
        current_post_categories = self.object.categories.all()  # Categories of the current post

        # Try fetching the tags safely
        try:
            current_post_tags = self.object.tags.all()  # Tags of the current post
        except AttributeError:
            # If tags cannot be found, fallback to an empty list or queryset
            current_post_tags = Tag.objects.none()

        # Debugging: Print or log current_post_tags to ensure it is being fetched correctly
        print(f"Current Post Tags: {current_post_tags}")
        # Recent posts, excluding the current one
        context['recent_posts'] = Post.objects.filter(published=True).exclude(id=self.object.id).order_by(
            '-created_at')[:2]
        context['tags'] = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        # Annotate the count of posts for each category
        context['categories'] = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        # Annotate the count of posts for each doctor (CustomUser)
        context['doctors'] = CustomUser.objects.filter(role='doctor').annotate(post_count=Count('posts')).order_by(
            '-post_count')
        # Annotate the count of posts for each disease
        context['diseases'] = Disease.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        current_post_categories = self.object.categories.all()

        post_diseases = self.object.related_diseases.all()
        related_doctors = CustomUser.objects.filter(
            doctorprofile__disease_specialization__in=post_diseases
        ).distinct()

        # Add related doctors to the context (including profile picture from BaseProfile)
        context['related_doctors'] = related_doctors.select_related('doctorprofile')

        # Fetch related posts in the same categories and tags (excluding the current post)
        context['related_posts'] = Post.objects.filter(
            Q(categories__in=current_post_categories) | Q(tags__in=current_post_tags),
            published=True
        ).exclude(id=self.object.id).distinct()[:3]
        # Fetch comments for the current post
        context['comments'] = post.comments.filter(parent__isnull=True).order_by(
            '-created_at')  # Show parent comments only

        # Pass the comment form (without post.id, because it's not part of the form fields)
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post  # Link the comment to the current post

            # Remove the user authentication check
            # Ensure the 'author_name' field is filled for anonymous users
            if not form.cleaned_data['author_name']:
                form.add_error('author_name', 'Name is required for anonymous comments.')
                return self.get(request, *args, **kwargs)

            # Save the comment after validation
            comment.save()

            # Redirect to the post detail page after successful comment submission
            return HttpResponseRedirect(reverse('blog:post-detail', kwargs={'pk': post.pk}))

        # If form is invalid, re-render the page with the form errors
        return self.get(request, *args, **kwargs)


class PostByTagView(ListView):
    model = Post
    template_name = 'others/articles/tag_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.filter(tags__name=self.kwargs['tag'], published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Annotate the count of posts for each tag
        context['tags'] = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        # Annotate the count of posts for each category
        context['categories'] = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        # Annotate the count of posts for each doctor (CustomUser)
        context['doctors'] = CustomUser.objects.filter(role='doctor').annotate(post_count=Count('posts')).order_by(
            '-post_count')
        # Annotate the count of posts for each disease
        context['diseases'] = Disease.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        context['selected_tag'] = self.kwargs['tag']
        return context


class PostByCategoryView(ListView):
    model = Post
    template_name = 'others/articles/category_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.filter(categories__name=self.kwargs['category'], published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Annotate the count of posts for each tag
        context['tags'] = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        # Annotate the count of posts for each category
        context['categories'] = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        # Annotate the count of posts for each doctor (CustomUser)
        context['doctors'] = CustomUser.objects.filter(role='doctor').annotate(post_count=Count('posts')).order_by(
            '-post_count')
        # Annotate the count of posts for each disease
        context['diseases'] = Disease.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        context['selected_category'] = self.kwargs['category']
        return context


class PostByDoctorView(ListView):
    model = Post
    template_name = 'others/articles/doctor_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        # Get the doctor profile (related to the user)
        doctor_profile = DoctorProfile.objects.get(user_id=self.kwargs['doctor_id'])

        # Get all diseases related to the doctor
        related_diseases = doctor_profile.disease_specialization.all()

        # Get all posts related to the diseases that this doctor specializes in
        return Post.objects.filter(related_diseases__in=related_diseases, published=True).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the doctor's full name to the context
        doctor_profile = DoctorProfile.objects.get(user_id=self.kwargs['doctor_id'])
        context['doctor_name'] = f"{doctor_profile.user.first_name} {doctor_profile.user.last_name}"
        # Annotate and add other context such as tags, categories, etc.
        context['tags'] = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        context['categories'] = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        context['doctors'] = CustomUser.objects.filter(doctorprofile__isnull=False).annotate(
            post_count=Count('posts')).order_by('-post_count')
        context['diseases'] = Disease.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        context['selected_doctor'] = doctor_profile.user  # Pass the doctor object to the template
        return context


class PostByDiseaseView(ListView):
    model = Post
    template_name = 'others/articles/related_disease_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        # Retrieve the disease based on the ID passed in the URL
        disease_id = self.kwargs['id']
        disease = Disease.objects.get(id=disease_id)
        return Post.objects.filter(related_diseases=disease)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Annotate the count of posts for each tag
        context['tags'] = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        # Annotate the count of posts for each category
        context['categories'] = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        # Annotate the count of posts for each doctor (CustomUser)
        context['doctors'] = CustomUser.objects.filter(role='doctor').annotate(post_count=Count('posts')).order_by(
            '-post_count')
        # Annotate the count of posts for each disease
        context['diseases'] = Disease.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        context['selected_disease'] = self.kwargs['id']  # For highlighting the selected disease
        return context


# Feed Views

class FeedListView(ListView):
    model = Feed
    template_name = 'blog/feeds/feeds.html'
    context_object_name = 'feeds'
    queryset = Feed.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Annotate the count of feeds for each tag
        context['tags'] = Tag.objects.annotate(feed_count=Count('feeds')).order_by('-feed_count')
        # Annotate the count of feeds for each category
        context['categories'] = Category.objects.annotate(feed_count=Count('feeds')).order_by('-feed_count')
        # Annotate the count of feeds for each disease
        context['diseases'] = Disease.objects.annotate(feed_count=Count('feeds')).order_by('-feed_count')
        # Featured feeds (you might need to adjust according to your model)
        context['featured_feeds'] = Feed.objects.filter(published=True, featured=True).order_by('-created_at')[:3]
        return context


class FeedDetailView(DetailView):
    model = Feed
    template_name = 'blog/feeds/feed.html'
    context_object_name = 'feed'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        feed = self.get_object()
        current_feed_categories = self.object.categories.all()
        current_feed_tags = self.object.tags.all()

        # Fetch recent feeds, excluding the current one
        context['recent_feeds'] = Feed.objects.filter(published=True).exclude(id=self.object.id).order_by('-created_at')[:2]
        context['tags'] = Tag.objects.annotate(feed_count=Count('feeds')).order_by('-feed_count')
        context['categories'] = Category.objects.annotate(feed_count=Count('feeds')).order_by('-feed_count')
        context['diseases'] = Disease.objects.annotate(feed_count=Count('feeds')).order_by('-feed_count')

        # Fetch related posts based on the diseases related to the current feed
        feed_diseases = self.object.diseases.all()
        related_posts = Post.objects.filter(
            Q(related_diseases__in=feed_diseases),
            published=True
        ).distinct()[:3]
        context['related_posts'] = related_posts[:3]

        # Fetch related feeds in the same categories and tags
        context['related_feeds'] = Feed.objects.filter(
            Q(categories__in=current_feed_categories) | Q(tags__in=current_feed_tags),
            published=True
        ).exclude(id=self.object.id).distinct()[:3]

        # Fetch comments for the current feed
        context['comments'] = feed.comments.filter(parent__isnull=True).order_by('-created_at')
        # Show parent comments only

        # Pass the comment form
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        feed = self.get_object()
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.feed = feed  # Link the comment to the current feed

            # Ensure the 'author_name' field is filled for anonymous comments
            if not form.cleaned_data.get('author_name'):
                form.add_error('author_name', 'Name is required for anonymous comments.')
                return self.get(request, *args, **kwargs)

            comment.save()

            # Redirect to the feed detail page after successful comment submission
            return HttpResponseRedirect(reverse('blog:feed-detail', kwargs={'pk': feed.pk}))

        # If form is invalid, re-render the page with the form errors
        return self.get(request, *args, **kwargs)


class FeedByCategoryView(ListView):
    model = Feed
    template_name = 'others/feeds/category_feeds.html'
    context_object_name = 'feeds'

    def get_queryset(self):
        category_id = self.kwargs['id']
        category = Category.objects.get(id=category_id)
        return Feed.objects.filter(categories=category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.annotate(feed_count=Count('feeds')).order_by('-feed_count')
        context['categories'] = Category.objects.annotate(feed_count=Count('feeds')).order_by('-feed_count')
        context['diseases'] = Disease.objects.annotate(feed_count=Count('feeds')).order_by('-feed_count')
        context['selected_category'] = self.kwargs['id']
        return context


class FeedByTagView(ListView):
    model = Feed
    template_name = 'others/feeds/tag_feeds.html'
    context_object_name = 'feeds'

    def get_queryset(self):
        tag_id = self.kwargs['id']
        tag = Tag.objects.get(id=tag_id)
        return Feed.objects.filter(tags=tag)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.annotate(feed_count=Count('feeds')).order_by('-feed_count')
        context['categories'] = Category.objects.annotate(feed_count=Count('feeds')).order_by('-feed_count')
        context['diseases'] = Disease.objects.annotate(feed_count=Count('feeds')).order_by('-feed_count')
        context['selected_tag'] = self.kwargs['id']
        return context


class FeedByDiseaseView(ListView):
    model = Feed
    template_name = 'others/feeds/diseases_feeds.html'
    context_object_name = 'feeds'

    def get_queryset(self):
        # Retrieve the disease based on the ID passed in the URL
        disease_id = self.kwargs['id']
        disease = Disease.objects.get(id=disease_id)
        return Feed.objects.filter(related_diseases=disease)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Annotate the count of feeds for each tag
        context['tags'] = Tag.objects.annotate(feed_count=Count('feeds')).order_by('-feed_count')
        # Annotate the count of feeds for each category
        context['categories'] = Category.objects.annotate(feed_count=Count('feeds')).order_by('-feed_count')
        # Annotate the count of feeds for each disease
        context['diseases'] = Disease.objects.annotate(feed_count=Count('feeds')).order_by('-feed_count')
        context['selected_disease'] = self.kwargs['id']  # For highlighting the selected disease
        return context
