from django import forms
from main import models
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class NewsDocumentForm(forms.ModelForm):
    class Meta:
        model = models.NewsDocumentsModel
        fields = ['news', 'name', 'document']


class NewsImageForm(forms.ModelForm):
    class Meta:
        model = models.ImagesModel
        fields = ['news', 'name', 'image', 'width', 'height']


class ReportDocumentForm(forms.ModelForm):
    class Meta:
        model = models.NewsDocumentsModel
        fields = ['report', 'name', 'document']


class ReportImageForm(forms.ModelForm):
    class Meta:
        model = models.ImagesModel
        fields = ['report', 'name', 'image', 'width', 'height']


class NewsAdminForm(forms.ModelForm):
    description = forms.CharField(label='Описание', widget=CKEditorUploadingWidget())

    class Meta:
        model = models.NewsModel
        fields = '__all__'
