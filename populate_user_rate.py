import os
import random

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "music.settings")

django.setup()
strs = 'abcdefghijk_mnopqrstuvwxyz'
from user.models import *


# 随机生成username
def random_user_name(length=5):
    return ''.join(random.choices(strs, k=length))


def random_phone():
    res = ''.join([str(random.randint(0, 9)) for _ in range(11)])
    return res


def random_music_id(num=5):
    book_nums = Music.objects.all().order_by('?').values('id')[:num]
    print(book_nums)
    return [book['id'] for book in book_nums]


def random_mark():
    return random.randint(1, 5)


def populate_user_rating(user_numbers):
    for i in range(user_numbers):
        user_name = random_user_name()
        print(user_name)
        try:
            user, created = User.objects.get_or_create(username=user_name,
                                                       name=user_name,
                                                       defaults={'password': user_name, "phone": random_phone(), "address": random_user_name(), "email": random_user_name() + '@163.com'})
            for music_id in random_music_id():
                Rate.objects.get_or_create(user=user, music_id=music_id, defaults={"mark": random_mark()})
        except Exception as e:
            raise e


if __name__ == '__main__':
    # random_music_id()
    # 随机生成用户打分 参数为生成数量
    populate_user_rating(2000)
