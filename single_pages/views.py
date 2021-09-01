from django.shortcuts import render
from board.models import Post
# Create your views here.

def landing(request):
    recent_posts = Post.objects.order_by('-pk')[:3]
    return render(
        request,
        'single_pages/landing.html',
        {
            'recent_posts': recent_posts,
        }
    )

def about_site(request):
    return render(
        request,
        'single_pages/about_site.html'
    )
