from django.contrib import admin
from .models import Document
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from import_export.fields import Field
from django.utils.html import format_html
import pytesseract
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.core.files.base import ContentFile
import os
import tempfile
from PyPDF2 import PdfMerger

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

class DocumentAdmin(ImportExportModelAdmin):
    resource_class = DocumentResource
    list_display = ('title', 'document_type', 'date', 'pdf_file_link', 'pdf_file_samoan_link')
    search_fields = ('title', 'content', 'document_type')
    
    def pdf_file_link(self, obj):
        if obj.pdf_file:
            return format_html('<a href="{}" target="_blank">View PDF</a>', obj.pdf_file.url)
        return "-"
    
    def pdf_file_samoan_link(self, obj):
        if obj.pdf_file_samoan:
            return format_html('<a href="{}" target="_blank">View Samoan PDF</a>', obj.pdf_file_samoan.url)
        return "-"
    
    pdf_file_link.short_description = 'PDF File'
    pdf_file_samoan_link.short_description = 'Samoan PDF File'

    def save_model(self, request, obj, form, change):
        # Create a temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Process pdf_file if it exists
            if 'pdf_file' in form.changed_data and obj.pdf_file:
                obj.pdf_file = self.process_pdf_with_ocr(obj.pdf_file, temp_dir)
            
            # Process pdf_file_samoan if it exists
            if 'pdf_file_samoan' in form.changed_data and obj.pdf_file_samoan:
                obj.pdf_file_samoan = self.process_pdf_with_ocr(obj.pdf_file_samoan, temp_dir)
        
        # Call the original save_model to save the object
        super().save_model(request, obj, form, change)

    def process_pdf_with_ocr(self, pdf_field, temp_dir):
        # Save the uploaded PDF to a temporary file
        pdf_path = os.path.join(temp_dir, 'input.pdf')
        with open(pdf_path, 'wb') as f:
            for chunk in pdf_field.chunks():
                f.write(chunk)
        
        # Convert PDF to images (one image per page)
        images = convert_from_path(pdf_path)
        
        # Initialize PDF merger for combining OCR-generated pages
        merger = PdfMerger()
        
        # Process each page
        for i, image in enumerate(images):
            # Perform OCR on the image to generate a searchable PDF page
            ocr_pdf_data = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
            
            # Save the OCR-generated PDF page to a temporary file
            temp_pdf_path = os.path.join(temp_dir, f'page_{i}.pdf')
            with open(temp_pdf_path, 'wb') as f:
                f.write(ocr_pdf_data)
            
            # Add the OCR-generated page to the merger
            merger.append(temp_pdf_path)
        
        # Save the merged PDF to a temporary file
        output_pdf_path = os.path.join(temp_dir, 'output.pdf')
        with open(output_pdf_path, 'wb') as f:
            merger.write(f)
        
        # Clean up the merger
        merger.close()
        
        # Read the new PDF and create a ContentFile
        with open(output_pdf_path, 'rb') as f:
            new_pdf = ContentFile(f.read(), name=pdf_field.name)
        
        return new_pdf

admin.site.register(Document, DocumentAdmin)