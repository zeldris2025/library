from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Document
from django.utils.html import format_html

class DocumentResource(resources.ModelResource):
    class Meta:
        model = Document
        fields = ('id', 'title', 'document_type', 'year', 'content', 'pdf_file')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True

@admin.register(Document)
class DocumentAdmin(ImportExportModelAdmin):
    resource_class = DocumentResource
    list_display = ('title', 'document_type', 'year', 'created_at', 'pdf_link')
    list_filter = ('document_type', 'year')
    search_fields = ('title', 'content')
    ordering = ('-year', 'title')
    date_hierarchy = 'created_at'
    fields = ('title', 'document_type', 'year', 'content', 'pdf_file')
    change_form_template = 'admin/documents/document/change_form.html'

    def pdf_link(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank">View PDF</a> | '
                '<button type="button" onclick="togglePDF(\'{}\', this)">Open Document</button>'
                '<div id="pdf-viewer-{}" style="display:none; margin-top:10px;">'
                '<iframe src="{}" width="100%" height="400px"></iframe>'
                '</div>',
                obj.pdf_file.url, obj.pdf_file.url, obj.id, obj.pdf_file.url
            )
        return 'No PDF'
    pdf_link.short_description = 'PDF'