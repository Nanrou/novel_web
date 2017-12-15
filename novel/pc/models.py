from django.db import models
from django.db.models import Q

from django_hosts.resolvers import reverse


# Create your models here.


class AuthorTable(models.Model):
    author = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.author


class CategoryTable(models.Model):
    cate = models.CharField(max_length=30, unique=True)
    category = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.category

    def get_absolute_url(self):
        return reverse('pc:category', kwargs={'cate': self.cate})

    def get_mobile_url(self):
        return reverse('wap:category', host='wap', kwargs={'cate': self.cate})


class BookTable(models.Model):
    title = models.CharField(max_length=70, unique=True)
    category = models.ForeignKey(CategoryTable, verbose_name='category', on_delete=models.CASCADE,
                                 related_name='cate_books')
    author = models.ForeignKey(AuthorTable, verbose_name='author', on_delete=models.CASCADE,
                               related_name='author_books')
    _status = models.BooleanField(default=0)
    update_time = models.DateTimeField(null=True)
    # store_des = models.IntegerField(verbose_name='book_table_index', null=True)
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

    @property
    def pure_resume(self):
        return self.resume.replace('<br/>', '').replace('【内容简介】', '')

    @classmethod
    def top_four_book(cls):
        q = Q()
        for book_id in [1, 74, 169, 170]:
            q.add(Q(**{'id': book_id}), Q.OR)
        return BookTable.objects.select_related('author').filter(q).only('title', 'author', 'resume', 'image', 'id')

    def get_absolute_url(self):
        return reverse('pc:book', kwargs={'pk': self.id})

    def get_mobile_url(self):
        return reverse('wap:book', host='wap', kwargs={'pk': self.id})


class ChapterTable(models.Model):
    title = models.ForeignKey(BookTable, verbose_name='title', on_delete=models.CASCADE, related_name='all_chapters')
    chapter = models.CharField(max_length=70)
    content = models.TextField()
    need_confirm = models.BooleanField(default=0)

    book_name = models.CharField(max_length=70, verbose_name='book_name')
    book_id = models.IntegerField(verbose_name='book_id')
    next_chapter_id = models.IntegerField(verbose_name='next_chapter_id', default=0)
    prev_chapter_id = models.IntegerField(verbose_name='prev_chapter_id', default=0)

    def __str__(self):
        return self.chapter

    def get_absolute_url(self):
        return reverse('pc:chapter', kwargs={'book_id': self.book_id, 'pk': self.id})

    def get_mobile_url(self):
        return reverse('wap:chapter', host='wap', kwargs={'book_id': self.book_id, 'pk': self.id})

    @property
    def next_chapter(self):
        if self.next_chapter_id == 0:
            return reverse('pc:book', kwargs={'pk': self.book_id})
        else:
            return reverse('pc:chapter', kwargs={'book_id': self.book_id, 'pk': self.next_chapter_id})

    @property
    def prev_chapter(self):
        if self.prev_chapter_id == 0:
            return reverse('pc:book', kwargs={'pk': self.book_id})
        else:
            return reverse('pc:chapter', kwargs={'book_id': self.book_id, 'pk': self.prev_chapter_id})

    @property
    def next_chapter_wap(self):
        if self.next_chapter_id == 0:
            return reverse('wap:book', host='wap', kwargs={'pk': self.book_id})
        else:
            return reverse('wap:chapter', host='wap', kwargs={'book_id': self.book_id, 'pk': self.next_chapter_id})

    @property
    def prev_chapter_wap(self):
        if self.prev_chapter_id == 0:
            return reverse('wap:book', host='wap', kwargs={'pk': self.book_id})
        else:
            return reverse('wap:chapter', host='wap', kwargs={'book_id': self.book_id, 'pk': self.prev_chapter_id})
