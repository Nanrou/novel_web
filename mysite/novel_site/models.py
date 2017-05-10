# -*- coding:utf-8 -*-

from django.db import models
from django.urls import reverse, reverse_lazy

# Create your models here.


class AuthorTable(models.Model):
    author = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.author


class CategoryTable(models.Model):
    cate = models.CharField(max_length=30, null=True, unique=True)
    category = models.CharField(max_length=20)

    def get_absolute_url(self):
        return reverse('novel_site:category', kwargs={'cate': self.cate})

    def __str__(self):
        return self.category


class InfoTable(models.Model):
    title = models.CharField(max_length=70, unique=True)
    category = models.ForeignKey(CategoryTable, verbose_name='category', on_delete=models.CASCADE,
                                 related_name='cate_books')
    author = models.ForeignKey(AuthorTable, verbose_name='author', on_delete=models.CASCADE,
                               related_name='author_boos')
    status = models.CharField(max_length=5)
    update_time = models.DateTimeField()
    store_des = models.IntegerField(verbose_name='book_table_index', null=True)
    image = models.CharField(max_length=70, verbose_name='image_des', null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('novel_site:info', kwargs={'pk': self.pk})

    @property
    def latest_chapter(self):
        return MAP_DICT[str(self.store_des)].objects.filter(title=self.pk).latest('id')

    @property
    def all_chapters(self):
        return MAP_DICT[str(self.store_des)].objects.filter(title=self.pk)


class Book(models.Model):
    title = models.ForeignKey(InfoTable, verbose_name='title', on_delete=models.CASCADE,)
    chapter = models.CharField(max_length=70, null=True)
    content = models.TextField()
    need_confirm = models.BooleanField(default=0)

    def get_absolute_url(self):
        return reverse('novel_site:detail', kwargs={'pk': self.title.pk, 'index': self.pk})

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
