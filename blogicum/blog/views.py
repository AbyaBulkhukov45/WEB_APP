from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PostForm, CommentForm
from django.urls import reverse_lazy,reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .forms import EditProfileForm
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Post, Category , Comment

POSTS_LIMIT = 4

class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    queryset = Post.objects.select_related('category', 'location').filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )
    ordering =  ['-pub_date']
    paginate_by = POSTS_LIMIT
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(comment_count=Count('comments'))
        return queryset


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html' 
    
    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        self.object = post
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context
    
  
class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    paginate_by = POSTS_LIMIT

    def get_queryset(self):
        category_slug = self.kwargs['slug']
        return Post.objects.filter(
            category__slug=category_slug,
            is_published=True).order_by('-pub_date')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs['slug']
        context['category'] = Category.objects.get(slug=category_slug)
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/delete.html'
    success_url = reverse_lazy('blog:index')
    
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(
            Post, pk=kwargs['pk'],
            author=request.user)
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        form.initial['pub_date'] = self.object.pub_date
        return self.render_to_response(
            self.get_context_data(form=form))
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('blog:index')


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, pk, comment_pk):
    post = get_object_or_404(Post, pk=pk)
    comment = get_object_or_404(Comment, pk=comment_pk)
    if comment.author != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', pk=pk)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/comment.html', {'form': form})


@login_required
def delete_comment(request, pk, comment_pk):
    post = get_object_or_404(Post, pk=pk)
    comment = get_object_or_404(Comment, pk=comment_pk)
    if comment.author != request.user:
        raise PermissionDenied
    comment.delete()
    return redirect('blog:post_detail', pk=pk)
  

class ProfileView(LoginRequiredMixin, ListView):
    template_name = 'blog/profile.html'
    context_object_name = 'posts'
    paginate_by = 4

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        return Post.objects.filter(author=user).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(User, username=self.kwargs['username'])
        return context
   

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'blog/edit_profile.html', {'form': form})
