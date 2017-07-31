import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

import django
django.setup()
from novel_site.models import InfoTable

xml_txt = '''
    <url>
        <loc><![CDATA[http://superxiaoshuo.com/info/{id}]]></loc>
        <lastmod>{update_time}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
        <data>
            <name>{book_name}</name>
            <author>
                <name>{author}</name>
            </author>
            <description><![CDATA[{chapter_name}]]></description>
            <genre>{category}</genre>
            <url><![CDATA[http://superxiaoshuo.com/info/{id}]]></url>
            <updateStatus>{status}</updateStatus>
            <trialStatus>免费</trialStatus>
            <newestChapter>
                <articleSection>{book_name}</articleSection>
                <headline>{chapter_name}</headline>
                <dateModified>{update_datetime}</dateModified>
                <url><![CDATA[http://superxiaoshuo.com{chapter_url}]]></url>
            </newestChapter>
            <chapter><headline>{chapter_name}</headline></chapter>
            <endingType>{category}</endingType>
            <collectedCount>999</collectedCount>
            <dateModified>{update_datetime}</dateModified>
        </data>
    </url>'''

with open('search_sitemap.xml', 'w', encoding='utf-8') as wf:
    wf.write('<?xml version="1.0" encoding="UTF-8"?><urlset>')

for i in range(1, 21):
    book = InfoTable.objects.get(id=i)
    with open('search_sitemap.xml', 'a', encoding='utf-8') as af:
        af.write(xml_txt.format(id=i, update_time=str(book.update_time).replace(' ', 'T'), book_name=book.title,
                                author=book.author, category=book.category, status=book.status,
                                chapter_name=book.latest_chapter, update_datetime=str(book.update_time).split(' ')[0],
                                chapter_url=book.latest_chapter.get_absolute_url(),))
else:
    with open('search_sitemap.xml', 'a', encoding='utf-8') as f:
        f.write('</urlset>')


