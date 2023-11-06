from django.urls import path

from . import views


app_name = 'blog'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('posts/<int:post_id>/',
         views.PostsDetail.as_view(), name='post_detail'),
    path('posts/create/', views.CreatePost.as_view(), name='create_post'),
    path('posts/<int:post_id>/edit/',
         views.PostEdit.as_view(), name='edit_post'),
    path('posts/<int:post_id>/delete/',
         views.PostDelete.as_view(), name='delete_post'),
    path('category/<slug:category_slug>/',
         views.CategoryPost.as_view(), name='category_posts'),
    path('posts/<int:post_id>/comment/',
         views.AddComment.as_view(), name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.EditComment.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.DeleteComment.as_view(), name='delete_comment'),
    path('profile/<str:username>/',
         views.Profile.as_view(), name='profile'),
    path('profile/<str:username>/edit/',
         views.EditProfile.as_view(), name='edit_profile'),
    path('profile/<str:username>/edit/password/',
         views.PasswordChange.as_view(), name='password_change'),
]
