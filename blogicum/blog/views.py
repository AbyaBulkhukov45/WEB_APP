from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
    CreateView,
    DeleteView,
)
from core.utils import post_all_query, post_published_query, get_post_data
from core.mixins import CommentMixinView
from .models import Post, User, Category, Comment
from .forms import UserEditForm, PostEditForm, CommentEditForm

POST_LIMIT = 10


class IndexView(ListView):
    model = Post
    template_name = "blog/index.html"
    queryset = post_published_query()
    paginate_by = POST_LIMIT


class CategoryPostListView(IndexView):
    template_name = "blog/category.html"

    def get_category(self):
        slug = self.kwargs["category_slug"]
        return get_object_or_404(Category, slug=slug, is_published=True)

    def get_queryset(self):
        category = self.get_category()
        return super().get_queryset().filter(category=category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_category()
        context["category"] = category
        return context


class UserPostsListView(IndexView):
    template_name = "blog/profile.html"

    def get_author(self):
        username = self.kwargs["username"]
        return get_object_or_404(User, username=username)

    def get_queryset(self):
        author = self.get_author()
        if author == self.request.user:
            return post_all_query().filter(author=author)
        return super().get_queryset().filter(author=author)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.get_author()
        context["profile"] = author
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"

    def get_post_data(self):
        return get_object_or_404(Post, pk=self.kwargs["pk"])

    def get_queryset(self):
        post_data = self.get_post_data()
        if post_data.author == self.request.user:
            return post_all_query().filter(pk=post_data.pk)
        return post_published_query().filter(pk=post_data.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_data = self.get_post_data()
        if self._check_post_data(post_data):
            context["flag"] = True
            context["form"] = CommentEditForm()
        context["comments"] = post_data.comments.all().select_related("author")
        return context

    def _check_post_data(self, post_data):
        return all(
            (
                post_data.is_published,
                post_data.pub_date <= now(),
                post_data.category.is_published,
            )
        )


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = "blog/user.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse("blog:profile",
                       kwargs={"username": self.request.user.username})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostEditForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:profile",
                       kwargs={"username": self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostEditForm
    template_name = "blog/create.html"

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.kwargs["pk"]})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/create.html"

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostEditForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse_lazy("blog:profile",
                            kwargs={"username": self.request.user.username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentEditForm
    template_name = "blog/comment.html"

    def dispatch(self, request, *args, **kwargs):
        self.post_data = get_post_data(self.kwargs)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_data
        if self.post_data.author != self.request.user:
            self.send_author_email()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:post_detail",
                       kwargs={"pk": self.kwargs["pk"]})

    def send_author_email(self):
        post_url = self.request.build_absolute_uri(self.get_success_url())
        recipient_email = self.post_data.author.email
        subject = "Новый комментарий"
        message = (
            f"Пользователь {self.request.user} добавил "
            f"комментарий к посту {self.post_data.title}.\n"
            f"Читать комментарий {post_url}"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email="from@example.com",
            recipient_list=[recipient_email],
            fail_silently=True,
        )


class CommentUpdateView(CommentMixinView, UpdateView):
    form_class = CommentEditForm


class CommentDeleteView(CommentMixinView, DeleteView):
    ...
