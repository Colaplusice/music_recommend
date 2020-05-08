# 添加和读取数据到数据库中
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "music.settings")

django.setup()
from user.models import Music, Tags
import csv

Music.objects.all().delete()
Tags.objects.all().delete()
opener = open('cloudmusic.csv', 'r', encoding='utf-8')
# opener.readline()
opener.readline()
reader = csv.reader(opener)
next(reader)
count = 0
for line in reader:
    if len(line) != 11:
        continue
    count += 1
    artist_id, artist_name, img_url, album_num, album_size, song_name, song_id, album_name, album_id, publish_time, lyric = line
    Music.objects.get_or_create(name=song_name, defaults={'artist': artist_name, "pic": img_url, 'album': album_name, 'lyric': lyric, 'years': publish_time})
    print('success')
    if count > 10000:
        break
