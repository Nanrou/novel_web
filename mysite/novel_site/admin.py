from django.contrib import admin
from .models import InfoTable, CategoryTable, BookTableOne

# Register your models here.


class CategoryTableAdmin(admin.ModelAdmin):
    list_display = ('category', 'counts')
    ordering = ('id', )

    def counts(self, obj):
        if obj.pk is 6:
            return InfoTable.objects.filter(_status=1).only('_status').count()
        return obj.cate_books.count()
    counts.short_description = 'cate_book_num'


class BookInline(admin.TabularInline):
    model = BookTableOne

    def view_on_site(self, obj):
        url = 'http://superxiaoshuo.dev:8000/adminnovel_site/booktableone/{}/change/'.format(str(obj.pk))
        return url

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.defer('content')

    fields = ('chapter', 'need_confirm')
    readonly_fields = ('chapter', 'need_confirm')


class InfoTableAdmin(admin.ModelAdmin):
    list_display = ('order_title', 'category', 'format_update_time')
    list_select_related = ('category', )
    search_fields = ('title', 'category')
    empty_value_display = '--empty--'
    ordering = ('id', )

    def order_title(self, obj):
        return obj.title
    order_title.admin_order_field = 'id'
    order_title.short_description = 'title'

    def format_update_time(self, obj):
        if obj.update_time is None:
            return obj.update_time
        # return '{:%Y-%m-%d %H:%M:%S}'.format(obj.update_time)
        return obj.update_time.strftime('%Y-%m-%d %H:%M:%S')
    format_update_time.short_description = 'update_time'
    format_update_time.admin_order_field = 'update_time'

    # inlines = (BookInline, )


class BookTableAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'chapter', 'need_confirm')
    list_select_related = ('title', )
    list_per_page = 20
    search_fields = ('id', )

    readonly_fields = ('book_id', 'title')


admin.site.register(InfoTable, InfoTableAdmin)
admin.site.register(CategoryTable, CategoryTableAdmin)
admin.site.register(BookTableOne, BookTableAdmin)
