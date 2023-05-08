from django.contrib import admin
from main import models
from main import forms


class DocumentsAdmin(admin.ModelAdmin):
    list_display = ('name', 'year')
    list_display_links = ('name', 'year')


class YearAdmin(admin.ModelAdmin):
    list_display = ('year',)
    list_display_links = ('year',)


class NewsImagesAdmin(admin.TabularInline):
    model = models.ImagesModel
    extra = 1
    form = forms.NewsImageForm


class NewsDocumentsAdmin(admin.TabularInline):
    model = models.NewsDocumentsModel
    extra = 1
    form = forms.NewsDocumentForm


class NewsAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    list_display_links = ('name', 'date')
    inlines = [NewsImagesAdmin, NewsDocumentsAdmin]
    form = forms.NewsAdminForm


class ReportImagesAdmin(admin.TabularInline):
    model = models.ImagesModel
    extra = 1
    form = forms.ReportImageForm


class ReportDocumentsAdmin(admin.TabularInline):
    model = models.NewsDocumentsModel
    extra = 1
    form = forms.ReportDocumentForm


class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    list_display_links = ('name', 'date')
    inlines = [ReportImagesAdmin, ReportDocumentsAdmin]


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
admin.site.register(models.ReportsModel, ReportAdmin)
