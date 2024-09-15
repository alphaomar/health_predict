from django.urls import path
from .views import IndexView, PostListView, PostDetailView, PostByTagView, PostByCategoryView, PostByDoctorView, \
    PostByDiseaseView, FeedListView, FeedDetailView, FeedByCategoryView, FeedByDiseaseView, FeedByTagView

app_name = 'blog'

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('posts', PostListView.as_view(), name='post-list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('tag/<str:tag>/posts/', PostByTagView.as_view(), name='tag_posts'),
    path('category/<str:category>/', PostByCategoryView.as_view(), name='category_posts'),
    path('doctor/<int:doctor_id>/', PostByDoctorView.as_view(), name='doctor_posts'),
    path('disease/<int:id>/', PostByDiseaseView.as_view(), name='disease_posts'),
    # feeds url
    path('feeds/', FeedListView.as_view(), name='feed-list'),
    path('feed/<int:pk>', FeedDetailView.as_view(), name='feed-detail'),
    path('feed/category/<int:id>/', FeedByCategoryView.as_view(), name='category-feeds'),
    path('feed/disease/<int:id>/', FeedByDiseaseView.as_view(), name='disease-feeds'),
    path('feed/tag/<int:id>', FeedByTagView.as_view(), name='tag-feeds')
]
