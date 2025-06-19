from django.contrib import admin
from .models import Document
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from import_export.fields import Field
from django.utils.html import format_html

class DocumentResource(resources.ModelResource):
    title = Field(attribute='title', column_name='title')
    content = Field(attribute='content', column_name='content')
    document_type = Field(attribute='document_type', column_name='document_type')
    date = Field(attribute='date', column_name='date')
    pdf_file = Field(attribute='pdf_file', column_name='pdf_file')
    pdf_file_samoan = Field(attribute='pdf_file_samoan', column_name='pdf_file_samoan')
    
    class Meta:
        model = Document
        fields = ('title', 'content', 'document_type', 'date', 'pdf_file', 'pdf_file_samoan')
        import_id_fields = ('title',)
        skip_unchanged = True
        report_skipped = True

@admin.register(Document)
class DocumentAdmin(ImportExportModelAdmin):
    resource_class = DocumentResource
    list_display = ('title', 'document_type','date', 'pdf_file_link', 'pdf_file_samoan_link')
    list_filter = ('document_type', 'date')
    search_fields = ('title', 'content')
    
    def pdf_file_link(self, obj):
        if obj.pdf_file:
            return format_html('<a href="{}" target="_blank">View English PDF</a>', obj.pdf_file.url)
        return "No English PDF"
    pdf_file_link.short_description = 'English PDF'
    
    def pdf_file_samoan_link(self, obj):
        if obj.pdf_file_samoan:
            return format_html('<a href="{}" target="_blank">View Samoan PDF</a>', obj.pdf_file_samoan.url)
        return "No Samoan PDF"
    pdf_file_samoan_link.short_description = 'Samoan PDF'