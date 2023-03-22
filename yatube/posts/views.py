from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm
from .models import Post, Group, User
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required


POST_QUANTITY = 10


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:POST_QUANTITY]
    paginator = Paginator(posts, POST_QUANTITY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):

    username = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=username)
    total_num_posts = user_posts.count
    paginator = Paginator(user_posts, POST_QUANTITY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'username': username,
        'user_posts': user_posts,
        'page_obj': page_obj,
        'total_num_posts': total_num_posts
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    posts = post.author.posts.all()
    context = {
        'post': post,
        'posts': posts,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required()
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user)
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    instance=post,
                    files=request.FILES or None,
                    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True
    }
    return render(request, 'posts/create_post.html', context)
