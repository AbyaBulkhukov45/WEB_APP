from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('category/<slug:slug>/', views.CategoryPostsView.as_view(), name='category_posts'),
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('posts/<int:pk>/comment/add/', views.add_comment, name='add_comment'),
    path('posts/<int:pk>/comment/edit/<int:comment_pk>/', views.edit_comment, name='edit_comment'),
    path('posts/<int:pk>/comment/delete/<int:comment_pk>/', views.delete_comment, name='delete_comment'),
]
