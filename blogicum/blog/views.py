from django.utils import timezone
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, PasswordChangeForm, PostForm, UserForm
from .models import Category, Comment, Post, User
from .utils import filter_published, select_post_objects, get_post_data

SUM_POSTS = 10


class Index(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by: int = SUM_POSTS

    def get_queryset(self):
        return filter_published(
            select_post_objects(Post).filter(
                pub_date__lte=timezone.now(),
                category__is_published=True
            )
        ).order_by('-pub_date')


class PostsDetail(DetailView):
    form_class = CommentForm
    model = Post
    pk_url_kwarg = "post_id"

    def get_context_data(self, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        context = super().get_context_data(**kwargs)
        if post.author != self.request.user and not post.is_published:
            raise Http404
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.prefetch_related(
            'post'
        ).filter(
            post=post
        )
        return context


class CreatePost(LoginRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'blog/create_post.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:profile", args=[self.request.user])


class PermissionPost():
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect(
                'blog:post_detail',
                self.kwargs.get('post_id')
            )
        return super().dispatch(request, *args, **kwargs)


class PostEdit(PermissionPost, LoginRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'blog/create_post.html'
    pk_url_kwarg = "post_id"

    def get_object(self, **kwargs):
        return get_object_or_404(
            Post,
            pk=self.kwargs.get('post_id'),
        )

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class PostDelete(PermissionPost, LoginRequiredMixin, DeleteView,):
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create_post.html'
    pk_url_kwarg = "post_id"

    def get_object(self, **kwargs):
        return get_object_or_404(
            Post,
            pk=self.kwargs.get('post_id'),
        )


class CategoryPost(ListView):
    category = None
    model = Category
    template_name = 'blog/category.html'
    paginate_by: int = SUM_POSTS

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(
            Category,
            slug=kwargs['category_slug'],
            is_published=True,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return filter_published(select_post_objects(Post).filter(
            category=self.category.id,
            pub_date__lte=timezone.now(),
        )).order_by('-pub_date')


class AddComment(LoginRequiredMixin, CreateView):
    blog_post = None
    form_class = CommentForm
    model = Comment
    pk_url_kwarg = "post_id"

    def dispatch(self, request, *args, **kwargs):
        self.blog_post = get_post_data(kwargs)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.blog_post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class EditComment(LoginRequiredMixin, UpdateView):
    form_class = CommentForm
    model = Comment
    pk_url_kwarg = "post_id"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect('blog:post_detail', post_id=obj.id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class DeleteComment(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment_form.html'

    def get_object(self, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return get_object_or_404(
            Comment,
            pk=self.kwargs.get('comment_id'),
            post=post,
            author=self.request.user)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class Profile(ListView):
    template_name = 'blog/profile.html'
    paginate_by = SUM_POSTS
    model = User

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )

        if self.author != self.request.user:
            return filter_published(select_post_objects(Post).filter(
                author=self.author,
            )).order_by(
                '-pub_date')

        return select_post_objects(Post).filter(
            author=self.author
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['profile'] = self.author
        return context


class EditProfile(LoginRequiredMixin, UpdateView):
    form_class = UserForm
    user = None
    model = User
    template_name = 'blog/user.html'

    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(
            User,
            username=kwargs['username']
        )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.user.get_username()}
        )


class PasswordChange(EditProfile):
    form_class = PasswordChangeForm
    model = User
    template_name = 'registration/password_reset_form.html'
