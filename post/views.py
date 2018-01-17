# coding: utf-8

import math

from django.shortcuts import render, redirect

from post.models import Article, Comment

from django.core.cache import cache

from .helper import page_cache, record_count, get_top_n_articles
from .forms import CommentForm
from redis import Redis

from pickle import dumps,loads

@page_cache(5)
def home(request):
    # 获取总页数
    count = Article.objects.count()
    pages = math.ceil(count / 5)

    # 获取用户点击的当前页，默认第一页是1,get得到的是字符串，需要转换int
    page = int(request.GET.get('page', 1))
    # 转换成程序员要计算的页数0开始计算
    page = 0 if page < 1 or page >= (pages + 1) else (page - 1)

    # 要展示的文章的序号
    start = page * 5
    end = start + 5

    # 文章切片查找
    articles = Article.objects.all()[start:end]

    # 首页展示点击量最高的top10
    top10 = get_top_n_articles(10)

    # 首页展示评论量最高的top5
    # top10 = get_comments_n_articles(10)
    return render(request, 'home.html', {'articles': articles, 'page': page, 'pages': range(pages), 'top10': top10})




@page_cache(3)
@record_count()
def article(request):
    aid = int(request.GET.get('aid', 1))
    article = Article.objects.get(id=aid)
    comments = Comment.objects.filter(aid=aid)
    # 阅读文章，点击量+    -->    装饰器实现
    # record_click(aid)


    # 写在视图函数中的缓存是model级别的
    # key = 'jarticle-%s' % aid
    # # 去缓存中查找,没有的话数据库中查找
    # article = cache.get(key)
    # if article is None:
    #     print('去db中找')
    #     article = Article.objects.get(id=aid)
    #     # 存到缓存
    #     cache.set(key, article)
    #     # 从缓存中返给客户端
    # comments = Comment.objects.filter(aid=aid)
    return render(request, 'article.html', {'article': article, 'comments': comments})


def create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        article = Article.objects.create(title=title, content=content)
        return redirect('/post/article/?aid=%s' % article.id)
    else:
        return render(request, 'create.html')


def editor(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        aid = int(request.POST.get('aid'))

        article = Article.objects.get(id=aid)
        article.title = title
        article.content = content
        article.save()
        return redirect('/post/article/?aid=%s' % article.id)
    else:
        aid = int(request.GET.get('aid', 0))
        article = Article.objects.get(id=aid)
        return render(request, 'editor.html', {'article': article})


def comment(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        content = request.POST.get('content')
        aid = int(request.POST.get('aid'))

        Comment.objects.create(name=name, content=content, aid=aid)
        return redirect('/post/article/?aid=%s' % aid)
    return redirect('/post/home/')



def search(request):
    if request.method == 'POST':
        keyword = request.POST.get('keyword')
        articles = Article.objects.filter(content__contains=keyword)
        return render(request, 'home.html', {'articles': articles})






