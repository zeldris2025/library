from django.db import models
from django.core.exceptions import ValidationError
import PyPDF2
import os

def validate_pdf(file):
    if not file.name.lower().endswith('.pdf'):
        raise ValidationError('File must be a PDF.')
    try:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
        if not text.strip():
            raise ValidationError('PDF must contain extractable text (not scanned).')
    except Exception as e:
        raise ValidationError(f'Invalid PDF: {str(e)}')

from datetime import datetime 

def upload_to_path(instance, filename):
    today = datetime.today()
    return os.path.join(
        'documents', 'pdfs',
        str(today.year),
        str(today.month),   # This removes leading zero
        str(today.day),
        filename
    )

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('BIL', 'Bills'),
        ('ACT', 'Acts & Ordinances'),
        ('REG', 'Samoa Regulations'),
        ('ORD', 'Order Papers'),
        ('SUM', 'Parliamentary Summaries'),
        ('HAN', 'Hansards Debates | Green Daily'),
        ('COM', 'Parliamentary Committee Reports'),
        ('Jou', 'Journals'),
        ('CUE', 'Cue Papers'),
        ('COM', 'Parliamentary Committee Reports'),
        ('CON', 'Constitutional Convention Debates'),
        ('COV', 'Government Responses'),
        ('GAZ', 'Western Samoa Gazettes'),
    ]
    
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=3, choices=DOCUMENT_TYPES)
    date = models.DateField(null=True, blank=True)
    content = models.TextField()
    pdf_file = models.FileField(upload_to=upload_to_path, validators=[validate_pdf], blank=True, null=True)
    pdf_file_samoan = models.FileField(upload_to='documents/pdfs/%Y/%m/%d/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['document_type']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()}) - {self.date}"