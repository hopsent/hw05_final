import operator

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from posts.models import Follow, Post, Group
from posts.forms import PostForm, CommentForm


AMOUNT: int = 10
User = get_user_model()
CACHE_PERIOD = 20


@cache_page(CACHE_PERIOD, key_prefix="index_page")
def index(request):

    INDEX: int = 1

    posts = Post.objects.select_related("author", "group")
    page_obj = paginator(posts, request)
    context = {
        "page_obj": page_obj,
        "index": INDEX,
    }
    template = "posts/index.html"
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related("group")
    page_obj = paginator(posts, request)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    template = "posts/group_list.html"
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related("group")
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user, author=author)
    else:
        following = False
    page_obj = paginator(posts, request)
    context = {
        "page_obj": page_obj,
        "author": author,
        "following": following,
    }
    template = "posts/profile.html"
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.select_related("author", "post")
    form = CommentForm(request.POST or None)
    if form.is_valid():
        return redirect("posts/<int:post_id>/comment/", post_id=post_id)
    context = {
        "post": post,
        "comments": comments,
        "form": form,
    }
    template = "posts/post_detail.html"
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, "posts/create_post.html", {"form": form})
    create_post = form.save(commit=False)
    create_post.author = request.user
    create_post.save()
    return redirect("posts:profile", username=request.user)


@login_required
def post_edit(request, post_id):

    IS_EDIT: int = 1

    post = Post.objects.get(pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    author = post.author
    if author != request.user:
        return redirect("posts:post_detail", post_id=post_id)
    if not form.is_valid():
        return render(
            request,
            "posts/create_post.html",
            {
                "form": form,
                "is_edit": IS_EDIT,
            },
        )
    form.save()
    return redirect("posts:post_detail", post_id=post_id)


def paginator(posts, request):
    paginator = Paginator(posts, AMOUNT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):

    FOLLOW: int = 1

    user = request.user
    follows = Follow.objects.filter(user=user)
    posts = []
    for follow in follows:
        posts += follow.author.posts.select_related("author", "group")
    posts.sort(key=operator.attrgetter("pub_date"), reverse=True)
    page_obj = paginator(posts, request)
    context = {
        "page_obj": page_obj,
        "follow": FOLLOW,
    }
    template = "posts/follow.html"
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("posts:profile", username=username)
