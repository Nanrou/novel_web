# -*- coding:utf-8 -*-

from random import sample
import _datetime

from django.contrib.auth.models import User as Build_in_User
from django.conf import settings
from django.db import models
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.utils.timezone import now as django_now

from django_hosts.resolvers import reverse as hosts_reverse
from captcha.fields import CaptchaField

# Create your models here.


class AuthorTable(models.Model):
    author = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.author


class CategoryTable(models.Model):
    cate = models.CharField(max_length=30, unique=True)
    category = models.CharField(max_length=20)

    def get_absolute_url(self):
        # return reverse('novel_site:category', kwargs={'cate': self.cate})
        return hosts_reverse('novel_site:category', host='www', kwargs={'cate': self.cate})

    def get_mobile_url(self):
        return hosts_reverse('mobile:category', host='mobile', kwargs={'cate': self.cate})

    def get_random_ele(self, num):
        if self.pk is 6:
            try:
                res = sample(list(InfoTable.objects.select_related('author').filter(_status=True).only('title', 'author', 'resume')), num)
            except ValueError:
                res = InfoTable.objects.filter(_status=True).only('title', 'author', 'resume')
        else:
            try:
                res = sample(list(self.cate_books.all().select_related('author').only('title', 'author', 'resume')), num)
            except ValueError:
                res = self.cate_books.all().only('title', 'author', 'resume')
        return res

    def __str__(self):
        return self.category


class InfoTable(models.Model):
    title = models.CharField(max_length=70, unique=True)
    category = models.ForeignKey(CategoryTable, verbose_name='category', on_delete=models.CASCADE,
                                 related_name='cate_books', null=True)
    author = models.ForeignKey(AuthorTable, verbose_name='author', on_delete=models.CASCADE,
                               related_name='author_boos', null=True)
    _status = models.BooleanField(default=0)
    update_time = models.DateTimeField(null=True)
    store_des = models.IntegerField(verbose_name='book_table_index', null=True)
    image = models.CharField(max_length=70, verbose_name='image_des', null=True)
    resume = models.CharField(max_length=300, null=True)

    latest_chapter = models.CharField(max_length=70, null=True)
    latest_chapter_url = models.CharField(max_length=70, null=True)

    def __str__(self):
        return self.title

    @property
    def status(self):
        if self._status:
            return '完结'
        else:
            return '连载中'

    def get_absolute_url(self):
        return hosts_reverse('novel_site:info', host='www', kwargs={'pk': self.pk})

    def get_mobile_url(self):
        return hosts_reverse('mobile:info', host='mobile', kwargs={'pk': self.pk})

    # @property
    # def latest_chapter(self):
    #     return MAP_DICT[str(self.store_des)].objects.filter(title=self.pk)
    #       .defer('content', 'need_confirm').latest('id')

    @property
    def all_chapters(self):  # 看是否要放到view中去
        return MAP_DICT[str(self.store_des)].objects.filter(title=self.pk).defer('content', 'need_confirm')

    @property
    def all_chapters_detail(self):
        return MAP_DICT[str(self.store_des)].objects.filter(title=self.pk)

    @property
    def all_chapters_id_only(self):
        return MAP_DICT[str(self.store_des)].objects.filter(title=self.pk).only('id', 'book_id')

    @property
    def miss_img_path(self):
        return 'mobile/css/miss.jpg'


class Book(models.Model):
    title = models.ForeignKey(InfoTable, verbose_name='title', on_delete=models.CASCADE,)
    chapter = models.CharField(max_length=70, null=True)
    content = models.TextField()
    need_confirm = models.BooleanField(default=0)
    book_id = models.IntegerField(verbose_name='book_id', null=True)

    def get_absolute_url(self):
        # return reverse('novel_site:detail', kwargs={'pk': self.book_id, 'index': self.pk})
        return hosts_reverse('novel_site:detail', host='www', kwargs={'pk': self.book_id, 'index': self.pk})

    def get_mobile_url(self):
        # return reverse('novel_site:m_detail', kwargs={'pk': self.book_id, 'index': self.pk})
        return hosts_reverse('mobile:detail', host='mobile', kwargs={'pk': self.book_id, 'index': self.pk})

    class Meta:
        abstract = True


class BookTableOne(Book):

    def __str__(self):
        return self.chapter


class BookTableTwo(Book):
    def __str__(self):
        return self.chapter


class BookTableThree(Book):
    def __str__(self):
        return self.chapter

MAP_DICT = {'1': BookTableOne, '2': BookTableTwo, '3': BookTableThree}


STATUS_CHOICES = (
    ('0', '连载中'),
    ('1', '已完结'),
)


class FormTest(models.Model):
    author = models.CharField(max_length=20)
    title = models.CharField(max_length=50)
    chapter = models.CharField(max_length=50)
    content = models.CharField(max_length=200)
    update_time = models.DateField(default=django_now)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)

    def __str__(self):
        return self.title


class ProfileTable(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    _fav_books = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.owner.username + "'s profile"

    def add_book(self, book_id):
        tmp = self._fav_books
        if tmp:
            tmp = tmp.split(',')
        else:
            tmp = []
        if book_id in tmp:
            return
        tmp.append(book_id)
        self._fav_books = ','.join(tmp)
        self.save()
        return True

    def get_books(self):
        book_num_list = self._fav_books
        q = Q()
        if bool(book_num_list):
            for i in book_num_list.split(','):
                q.add(Q(**{'id': int(i)}), Q.OR)  # 动态赋值查询
            return InfoTable.objects.filter(q).only('title', 'id')
        else:
            return

    def remove_book(self, book_id):
        tmp = self._fav_books.split(',')
        assert book_id in tmp
        for i, k in enumerate(tmp):
            if k is book_id:
                tmp.pop(i)
                break
        self._fav_books = ','.join(tmp)
        self.save()
