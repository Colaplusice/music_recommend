from django.db import models
from django.db.models import Avg


class User(models.Model):
    username = models.CharField(max_length=128, unique=True, verbose_name="账号")
    password = models.CharField(max_length=128, verbose_name="密码")
    phone = models.CharField(max_length=128, verbose_name="手机号码")
    name = models.CharField(max_length=128, verbose_name="名字", unique=True)
    address = models.CharField(max_length=128, verbose_name="地址")
    email = models.EmailField(verbose_name="邮箱")

    class Meta:
        verbose_name_plural = "用户"
        verbose_name = "用户"

    def __str__(self):
        return self.name


class Tags(models.Model):
    name = models.CharField(max_length=128, verbose_name="标签", unique=True)

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"

    def __str__(self):
        return self.name


class Music(models.Model):
    tags = models.ManyToManyField(Tags, verbose_name='标签', blank=True)
    collect = models.ManyToManyField(User, verbose_name="收藏者", blank=True)
    sump = models.IntegerField(verbose_name="收藏人数", default=0)
    name = models.CharField(verbose_name="歌曲名称", max_length=128, unique=True)
    artist = models.CharField(verbose_name="歌手", max_length=128)
    album = models.CharField(verbose_name='专辑名称', max_length=128)
    years = models.CharField(verbose_name="年份", max_length=128)
    lyric = models.TextField(verbose_name="歌词")
    num = models.IntegerField(verbose_name="浏览量", default=0)
    pic = models.URLField(verbose_name="封面图片", max_length=256)

    class Meta:
        verbose_name = "歌曲"
        verbose_name_plural = "歌曲"

    def __str__(self):
        return self.name


class Rate(models.Model):
    music = models.ForeignKey(
        Music, on_delete=models.CASCADE, blank=True, null=True, verbose_name="歌曲id"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, verbose_name="用户id",
    )
    mark = models.FloatField(verbose_name="评分")
    create_time = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)

    @property
    def avg_mark(self):
        average = Rate.objects.all().aggregate(Avg('mark'))['mark__avg']
        return average

    class Meta:
        verbose_name = "评分信息"
        verbose_name_plural = verbose_name


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    content = models.CharField(max_length=64, verbose_name="内容")
    create_time = models.DateTimeField(auto_now_add=True)
    good = models.IntegerField(verbose_name="点赞", default=0)
    music = models.ForeignKey(Music, on_delete=models.CASCADE, verbose_name="歌曲")

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = verbose_name
