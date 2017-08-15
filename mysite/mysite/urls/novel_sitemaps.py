# -*- coding:utf-8 -*-


from django.contrib.sitemaps import Sitemap
from novel_site.models import InfoTable


class NovelSitemap(Sitemap):
    changefreq = 'daily'
    priority = 1.0

    def items(self):
        return InfoTable.objects.select_related('author', 'category')\
            .defer('resume', 'image', 'store_des', 'latest_chapter_url')\
            .order_by('id').all()

    def lastmod(self, obj):
        return obj.update_time

    def location(self, obj):
        return '/info/{}/'.format(obj.pk)








