# -*- coding:utf-8 -*-

from django.db import models
from django.urls import reverse

# Create your models here.

MAP_DICT = {'1': 'One', '2': 'Two', '3': 'Three'}


class AuthorTable(models.Model):
    author = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.author


class CategoryTable(models.Model):
    cate = models.CharField(max_length=30, null=True, unique=True)
    category = models.CharField(max_length=20)

    def __str__(self):
        return self.category


class InfoTable(models.Model):
    title = models.CharField(max_length=70, unique=True)
    category = models.ForeignKey(CategoryTable, verbose_name='category', on_delete=models.CASCADE,
                                 to_field='id', related_name='cate_books')
    author = models.ForeignKey(AuthorTable, verbose_name='author', on_delete=models.CASCADE,
                               to_field='author', related_name='author_boos')
    status = models.CharField(max_length=5)
    update_time = models.DateTimeField()
    store_des = models.IntegerField(verbose_name='book_table_index', null=True)

    def __str__(self):
        return self.title

    # def get_absolute_url(self):
    #     return reverse('info')
    @property
    def all_chapters(self):
        if self.status == '1':
            chapters = BookTableOne.objects.get(title=self.title)
            return chapters


class Book(models.Model):
    title = models.ForeignKey(InfoTable, verbose_name='title', on_delete=models.CASCADE)
    chapter = models.CharField(max_length=70, null=True)
    content = models.TextField()
    need_confirm = models.BooleanField(default=0)

    def get_absolute_url(self):
        return reverse('detail', args=[self.title.pk, self.id])

    class Meta:
        abstract = True


class BookTableOne(Book):

    def __str__(self):
        return 'book table 01'


class BookTableTwo(Book):
    def __str__(self):
        return 'book table 02'


class BookTableThree(Book):
    def __str__(self):
        return 'book table 03'
