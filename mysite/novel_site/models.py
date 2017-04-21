from django.db import models

# Create your models here.


class NovelTable(models.Model):
    chapter = models.CharField(max_length=70)
    modified_time = models.DateTimeField()
    content = models.CharField(max_length=15000)

    def __str__(self):
        return self.chapter
