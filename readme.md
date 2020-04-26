# 毕业设计--基于Django的歌曲推荐系统和论坛

## 说明

1. 新手建议结合pycharm使用，https://www.jetbrains.com/pycharm/，下载专业版试用30天。
2. 注册普通用户通过web界面来设置，创建创建用户通过creeatsuperuser创建。下文有详细命令
3. 导入歌曲信息通过insert_movies_script.py来操作 (会删除已有的所有信息!)
4. 前端展示 浏览最多，评分最多，收藏最多，写的比较直白，你可以改的委婉点: 最热歌曲，火爆排行...之类的。每种有10条。

我猜你喜欢为基于用户推荐，item推荐为基于项目推荐。两种推荐思路下文有介绍

## 系统采用的技术

前端: bootstrap3 css 框架
后端: django 2.2.1 + sqlite3数据库  (MVC框架)
数据: python异步爬虫从豆瓣top250抓取数据，保存到本地csv文件中
主要功能: 录入图书信息，用户打分，歌曲标签分类，歌曲推荐，歌曲分享，歌曲收藏，后台管理系统。
整体采用MVC架构，前端页面通过django template模板来实现，实现了模板的复用功能。同时前端页面的组织结构较为清晰。


## 推荐算法思路

通过协调过滤计算和其他用户的距离，然后进行筛选。如果用户数量不足，推荐数目不够15条，就会自动从
所有未打分的歌曲中按照浏览数降序选一部分填充进去。

### 基于用户的推荐

1. 用户需要给歌曲打分。通过用户已打分的部分来计算相似度,如果用户未打分，或者没有其他用户，则按照浏览数降序返回。
2. 通过pearson算法来计算用户之间的距离，找到距离最近的N个用户。将这些用户中已打分的歌曲(且要推荐的用户未看过的部分)返回。

### 基于item的推荐

1. 计算物品相似度矩阵: https://www.jianshu.com/p/27b1c035b693
2. 遍历当前用户已打分的item，计算和未打分的item的相似距离。
3. 对相似距离进行排序 返回

## 主要实现的功能

1.	登录注册页面
2.	基于协同过滤的歌曲的分类，排序，搜索，打分，排序功能。
3.	基于协同过滤的周推荐和月推荐
4. 观影分享会等活动功能，用户报名功能 (需要额外添加)
5. 发帖留言论坛功能 (要额外添加)
6. 基于spark的ALS算法 (要额外添加)
7. Mysql适配
8. movielens数据集适配

## 参考链接

[推荐算法—协同过滤 - 简书](https://www.jianshu.com/p/5463ab162a58)
[协同过滤和基于内容推荐有什么区别？ - 知乎](https://www.zhihu.com/question/19971859)


## fixed

1. 首页导航栏链接错误
2. 首页面为空
3. 登录注册页面
4. 推荐跳转登录
5. 周推荐用户没有评分时随机推荐
6. 按照收藏数量排序
7. 重新设计了 action 和UserAction model，拆分出了UserAction

## 歌曲模型

1. 浏览量 每次刷新页面的浏览数
2. 收藏量 user manytomany field 每个用户收藏一次
3. 评分   rate 每个用户评分一次
4. 在歌曲下面的评论加点赞功能

## 安装运行方法

## 安装依赖

1. 将项目导入pycharm, 在pycharm配置python解释器，3.7及以下都可以。可以通过conda或者其他的虚拟环境来安装
2. 打开终端 输入pip install -r requirements.txt  若提示无pip。去下载get-pip.py 运行python get-pip.py
3. 在pip安装过程中如果报错C++ 14依赖问题。则安装c++依赖工具。找不到找我要。如果安装速度过慢，请更换国内镜像https://blog.csdn.net/chenghuikai/article/details/55258957
4. 安装成功后，进入运行阶段

## 运行

1. 运行服务器: python manage.py runserver
2. 如果无数据，运行项目根目录下的数据迁移脚本 populate开头。
3. python manage.py createsuperuser 创建超级管理员, (密码输入时终端暂时看不到)
4. 进入后台: 127.0.0.1:8000/admin

需要获得永久更新和维护支持请联系我
其他问题请联系我

## 各文件功能

1. media/ 静态文件存放处，图片
2. movie/ Django的默认app，负责设置的配置还有url路由,部署等功能
3. static/ css文件和js文件的存放处
4. user/ 主app，程序的所有代码基本都在这下面 user/migrations为自动生成的数据库迁移文件 user/templates为前端页面模板文件，
user/admins.py 为管理员后台代码 user/forms.py为前端表单代码 user/models.py为数据库orm模型 user/serializers.py为restful文件，不用管。 user/urls为路由注册文件。 user/views为负责处理前端请求和与后端数据库交互的模块，也就是controller模块。
5. cache_keys.py为缓存的key值名称存放文件，不用管。
6. db.sqlite3数据库文件
7. douban_crawler.py 豆瓣爬虫文件
8. manage.py 运行的主程序，从这里启动
9. populate_movies_script.py 填充歌曲数据到数据库中
10. populate_user_rate.py  随机生成用户评分

