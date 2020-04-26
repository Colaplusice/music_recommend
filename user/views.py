import logging
from functools import wraps

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.renderers import JSONRenderer

from cache_keys import USER_CACHE, ITEM_CACHE
from recommend_musics import recommend_by_user_id, recommend_by_item_id
from .forms import *

logger = logging.getLogger()
logger.setLevel(level=0)


def login_in(func):  # 验证用户是否登录
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        is_login = request.session.get("login_in")
        if is_login:
            return func(*args, **kwargs)
        else:
            return redirect(reverse("login"))

    return wrapper


def musics_paginator(musics, page):
    paginator = Paginator(musics, 6)
    if page is None:
        page = 1
    musics = paginator.page(page)
    return musics


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs["content_type"] = "application/json"
        super(JSONResponse, self).__init__(content, **kwargs)


def login(request):
    if request.method == "POST":
        form = Login(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            result = User.objects.filter(username=username)
            if result:
                user = User.objects.get(username=username)
                if user.password == password:
                    request.session["login_in"] = True
                    request.session["user_id"] = user.id
                    request.session["name"] = user.name
                    return redirect(reverse("all_music"))
                else:
                    return render(
                        request, "user/login.html", {"form": form, "message": "密码错误"}
                    )
            else:
                return render(
                    request, "user/login.html", {"form": form, "message": "账号不存在"}
                )
    else:
        form = Login()
        return render(request, "user/login.html", {"form": form})


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        error = None
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password2"]
            email = form.cleaned_data["email"]
            name = form.cleaned_data["name"]
            phone = form.cleaned_data["phone"]
            address = form.cleaned_data["address"]
            User.objects.create(
                username=username,
                password=password,
                email=email,
                name=name,
                phone=phone,
                address=address,
            )
            # 根据表单数据创建一个新的用户
            return redirect(reverse("login"))  # 跳转到登录界面
        else:
            return render(
                request, "user/register.html", {"form": form, "error": error}
            )  # 表单验证失败返回一个空表单到注册页面
    form = RegisterForm()
    return render(request, "user/register.html", {"form": form})


def logout(request):
    if not request.session.get("login_in", None):  # 不在登录状态跳转回首页
        return redirect(reverse("index"))
    request.session.flush()  # 清除session信息
    return redirect(reverse("index"))


def all_music(request):
    musics = Music.objects.annotate(user_collector=Count('collect')).order_by('-user_collector')
    paginator = Paginator(musics, 9)
    current_page = request.GET.get("page", 1)
    musics = paginator.page(current_page)
    return render(request, "user/item.html", {"musics": musics, "title": "所有歌曲"})


def search(request):  # 搜索
    if request.method == "POST":  # 如果搜索界面
        key = request.POST["search"]
        request.session["search"] = key  # 记录搜索关键词解决跳页问题
    else:
        key = request.session.get("search")  # 得到关键词
    musics = Music.objects.filter(
        Q(name__icontains=key) | Q(lyric__icontains=key) | Q(artist__icontains=key)
    )  # 进行内容的模糊搜索
    page_num = request.GET.get("page", 1)
    musics = musics_paginator(musics, page_num)
    return render(request, "user/item.html", {"musics": musics})


def music(request, music_id):
    music = Music.objects.get(pk=music_id)
    music.num += 1
    music.save()
    comments = music.comment_set.order_by("-create_time")
    user_id = request.session.get("user_id")
    music_rate = Rate.objects.filter(music=music).all().aggregate(Avg('mark'))
    if music_rate:
        music_rate = music_rate['mark__avg']
    if user_id is not None:
        user_rate = Rate.objects.filter(music=music, user_id=user_id).first()
        user = User.objects.get(pk=user_id)
        is_collect = music.collect.filter(id=user_id).first()
    return render(request, "user/music.html", locals())


@login_in
# 在打分的时候清楚缓存
def score(request, music_id):
    user_id = request.session.get("user_id")
    # user = User.objects.get(id=user_id)
    music = Music.objects.get(id=music_id)
    score = float(request.POST.get("score"))
    get, created = Rate.objects.get_or_create(user_id=user_id, music=music, defaults={"mark": score})
    if created:
        print('create data')
        # 清理缓存
        user_cache = USER_CACHE.format(user_id=user_id)
        item_cache = ITEM_CACHE.format(user_id=user_id)
        cache.delete(user_cache)
        cache.delete(item_cache)
        print('cache deleted')

    return redirect(reverse("music", args=(music_id,)))


@login_in
def commen(request, music_id):
    user = User.objects.get(id=request.session.get("user_id"))
    music = Music.objects.get(id=music_id)
    # music.score.com += 1
    # music.score.save()
    comment = request.POST.get("comment")
    Comment.objects.create(user=user, music=music, content=comment)
    return redirect(reverse("music", args=(music_id,)))


def good(request, commen_id, music_id):
    commen = Comment.objects.get(id=commen_id)
    commen.good += 1
    commen.save()
    return redirect(reverse("music", args=(music_id,)))


@login_in
def collect(request, music_id):
    user = User.objects.get(id=request.session.get("user_id"))
    music = Music.objects.get(id=music_id)
    music.collect.add(user)
    music.save()
    return redirect(reverse("music", args=(music_id,)))


@login_in
def decollect(request, music_id):
    user = User.objects.get(id=request.session.get("user_id"))
    music = Music.objects.get(id=music_id)
    music.collect.remove(user)
    # music.rate_set.count()
    music.save()
    return redirect(reverse("music", args=(music_id,)))


@login_in
def personal(request):
    user = User.objects.get(id=request.session.get("user_id"))
    if request.method == "POST":
        form = Edit(instance=user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("personal"))
        else:
            return render(
                request, "user/personal.html", {"message": "修改失败", "form": form}
            )
    form = Edit(instance=user)
    return render(request, "user/personal.html", {"form": form})


@login_in
def mycollect(request):
    user = User.objects.get(id=request.session.get("user_id"))
    music = user.music_set.all()
    return render(request, "user/mycollect.html", {"music": music})


@login_in
def myjoin(request):
    user_id = request.session.get("user_id")
    user = User.objects.get(id=user_id)
    user_actions = user.action_set.all()
    return render(request, "user/myaction.html", {"action": user_actions})


@login_in
def my_comments(request):
    user = User.objects.get(id=request.session.get("user_id"))
    comments = user.comment_set.all()
    print('comment:', comments)
    return render(request, "user/my_comment.html", {"comments": comments})


@login_in
def delete_comment(request, comment_id):
    Comment.objects.get(pk=comment_id).delete()
    return redirect(reverse("my_comments"))


@login_in
def my_rate(request):
    user = User.objects.get(id=request.session.get("user_id"))
    rate = user.rate_set.all()
    return render(request, "user/my_rate.html", {"rate": rate})


def delete_rate(request, rate_id):
    Rate.objects.filter(pk=rate_id).delete()
    return redirect(reverse("my_rate"))


def hot_music(request):
    page_number = request.GET.get("page", 1)
    musics = Music.objects.annotate(user_collector=Count('collect')).order_by('-user_collector')[:10]
    musics = musics_paginator(musics[:10], page_number)
    return render(request, "user/item.html", {"musics": musics, "title": "最热歌曲"})


# 评分最多
def most_mark(request):
    page_number = request.GET.get("page", 1)
    musics = Music.objects.all().annotate(num_mark=Count('rate')).order_by('-num_mark')[:10]
    musics = musics_paginator(musics, page_number)
    return render(request, "user/item.html", {"musics": musics, "title": "评分最多"})


# 浏览最多
def most_view(request):
    page_number = request.GET.get("page", 1)
    musics = Music.objects.annotate(user_collector=Count('num')).order_by('-num')[:10]
    musics = musics_paginator(musics[:10], page_number)
    return render(request, "user/item.html", {"musics": musics, "title": "浏览最多"})


def latest_music(request):
    page_number = request.GET.get("page", 1)
    musics = musics_paginator(Music.objects.order_by("-id")[:10], page_number)
    return render(request, "user/item.html", {"musics": musics, "title": "最新歌曲"})


def golden_horse(request):
    page_number = request.GET.get("page", 1)
    music_cate = "金马奖"
    musics = musics_paginator(Music.objects.filter(good=music_cate), page_number)
    return render(request, "user/item.html", {"musics": musics, "title": music_cate})


def oscar(request):
    page_number = request.GET.get("page", 1)
    music_cate = "奥斯卡奖"
    musics = musics_paginator(Music.objects.filter(good=music_cate), page_number)
    return render(request, "user/item.html", {"musics": musics, "title": music_cate})


def begin(request):
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]
        result = User.objects.filter(username=username)
        if result:
            if result[0].email == email:
                result[0].password = request.POST["password"]
                return HttpResponse("修改密码成功")
            else:
                return render(request, "user/begin.html", {"message": "注册时的邮箱不对"})
        else:
            return render(request, "user/begin.html", {"message": "账号不存在"})
    return render(request, "user/begin.html")


def kindof(request):
    tags = Tags.objects.all()
    return render(request, "user/kindof.html", {"tags": tags})


def kind(request, kind_id):
    tags = Tags.objects.get(id=kind_id)
    musics = tags.music_set.all()
    page_num = request.GET.get("page", 1)
    musics = musics_paginator(musics, page_num)
    return render(request, "user/item.html", {"musics": musics})


@login_in
def reco_by_week(request):
    page = request.GET.get("page", 1)
    user_id = request.session.get("user_id")
    cache_key = USER_CACHE.format(user_id=user_id)
    music_list = cache.get(cache_key)
    if music_list is None:
        music_list = recommend_by_user_id(user_id)
        cache.set(cache_key, music_list, 60 * 5)
    else:
        logger.info('user {}缓存命中!'.format(user_id))
    musics = musics_paginator(music_list, page)
    path = request.path
    title = "周推荐歌曲"
    return render(
        request, "user/item.html", {"musics": musics, "path": path, "title": title}
    )


@login_in
def item_recommend(request):
    page = request.GET.get("page", 1)
    user_id = request.session.get("user_id")
    cache_key = ITEM_CACHE.format(user_id=user_id)
    music_list = cache.get(cache_key)
    if music_list is None:
        music_list = recommend_by_item_id(user_id)
        cache.set(cache_key, music_list, 60 * 5)
        print('设置缓存')
    else:
        print('缓存命中!')
    musics = musics_paginator(music_list, page)
    path = request.path
    title = "依据item推荐"
    return render(
        request, "user/item.html", {"musics": musics, "path": path, "title": title}
    )
