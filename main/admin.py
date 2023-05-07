from django.contrib import admin
from main import models


class DocumentsAdmin(admin.ModelAdmin):
    list_display = ('name', 'year')
    list_display_links = ('name', 'year')


class YearAdmin(admin.ModelAdmin):
    list_display = ('year',)
    list_display_links = ('year',)


class NewsImagesAdmin(admin.TabularInline):
    model = models.ImagesModel
    extra = 1


class NewsDocumentsAdmin(admin.TabularInline):
    model = models.NewsDocuments
    extra = 1


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    list_display_links = ('title', 'date')
    inlines = [NewsImagesAdmin, NewsDocumentsAdmin]


class ResultsAdmin(admin.ModelAdmin):
    list_display = ('tournament_name', 'date')
    list_display_links = ('tournament_name', 'date')


class CalendarAdmin(admin.ModelAdmin):
    list_display = ('competition', 'date_start', 'date_finish')
    list_display_links = ('competition', 'date_start', 'date_finish')


admin.site.register(models.DocumentModel, DocumentsAdmin)
admin.site.register(models.YearModel, YearAdmin)
admin.site.register(models.NewsModel, NewsAdmin)
admin.site.register(models.ResultsModel, ResultsAdmin)
admin.site.register(models.CalendarModel, CalendarAdmin)
