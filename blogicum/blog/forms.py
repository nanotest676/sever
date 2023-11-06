from django.contrib.auth import get_user_model
from django import forms

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author', 'created_at',)


class CommentForm(forms.ModelForm):
    class Meta:
        fields = ('text',)
        model = Comment


class UserForm(forms.ModelForm):
    class Meta:
        fields = ('email', 'first_name', 'last_name',)
        model = User


class PasswordChangeForm(forms.ModelForm):
    class Meta:
        fields = ('password',)
        model = User
