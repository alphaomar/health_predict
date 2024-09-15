from django.db import models
from django.db.models import Count


class PostManager(models.Manager):
    def latest_posts(self):
        # Filter for published posts and order by created date (most recent first)
        return self.filter(published=True).order_by('-created_at')

    def popular_posts(self, limit=10):
        # Annotate posts with comment counts and order by comment count (most popular first)
        return self.filter(published=True).annotate(comment_count=Count('comments')).order_by('-comment_count')[
               :limit]
