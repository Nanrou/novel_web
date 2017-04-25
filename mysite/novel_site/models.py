# -*- coding:utf-8 -*-

from django.db import models
from django.urls import reverse

# Create your models here.


class NovelTable(models.Model):
    chapter = models.CharField(max_length=70)
    modified_time = models.DateTimeField()
    need_confirm = models.BooleanField(default=0)
    content = models.CharField(max_length=15000)  # 以后直接同textfield

    def __str__(self):
        return self.chapter

    def get_absolute_url(self):
        return reverse('novel_site:detail', kwargs={'pk': self.pk})

    def get_next_url(self):
        try:
            next_id = int(self.pk) + 1
            return reverse('novel_site:detail', kwargs={'pk': next_id})
        except ValueError:  # 增加跳回主页的异常处理
            return '/'

    def get_last_url(self):
        try:
            last_id = int(self.pk) - 1
            if last_id < 0:
                return '/'
            return reverse('novel_site:detail', kwargs={'pk': last_id})
        except ValueError:
            return '/'
