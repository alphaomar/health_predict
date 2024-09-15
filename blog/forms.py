from django import forms
from .models import Category, Tag, Disease, Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['parent', 'author_name', 'content']
        labels = {
            'content': 'Comment',
            'author_name': 'Name',
            'author': 'Author'
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'comment-form textarea',  # Custom CSS class
                'rows': 4,
                'placeholder': 'Write your comment here...',  # Placeholder text
            }),
            'author_name': forms.TextInput(attrs={
                'class': 'comment_form input',
                'placeholder': 'Enter name',
            }),
            'parent': forms.HiddenInput(),  # Keep the parent field hidden for replies
        }

    # Optionally add a hidden input for parent comment when replying
    parent = forms.ModelChoiceField(queryset=Comment.objects.all(), required=False, widget=forms.HiddenInput)
