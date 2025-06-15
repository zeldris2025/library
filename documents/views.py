from django.shortcuts import render, get_object_or_404
from .models import Document
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import PyPDF2
import os

def document_list(request):
    documents = Document.objects.all()
    search_query = request.GET.get('q', '')
    selected_type = request.GET.get('type', '')
    selected_letter = request.GET.get('letter', '')
    selected_year = request.GET.get('year', '')
    
    if search_query:
        # Search title and content
        documents = documents.filter(title__icontains=search_query) | documents.filter(content__icontains=search_query)
        
        # Search PDF content
        pdf_matches = []
        for document in documents:
            if document.pdf_file:
                try:
                    pdf_path = document.pdf_file.path
                    with open(pdf_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ''
                        for page in reader.pages:
                            extracted = page.extract_text() or ''
                            text += extracted
                        if search_query.lower() in text.lower():
                            pdf_matches.append(document.id)
                except Exception:
                    continue
        if pdf_matches:
            documents = documents.filter(id__in=pdf_matches) | documents.filter(title__icontains=search_query) | documents.filter(content__icontains=search_query)
    
    if selected_type:
        documents = documents.filter(document_type=selected_type)
    if selected_letter:
        documents = documents.filter(title__istartswith=selected_letter)
    if selected_year:
        documents = documents.filter(year=selected_year)
    
    paginator = Paginator(documents, 20)  # 20 documents per page
    page = request.GET.get('page')
    try:
        documents = paginator.page(page)
    except PageNotAnInteger:
        documents = paginator.page(1)
    except EmptyPage:
        documents = paginator.page(paginator.num_pages)
    
    document_types = Document.DOCUMENT_TYPES
    letters = [chr(i) for i in range(65, 91)]  # A-Z
    years = Document.objects.values_list('year', flat=True).distinct().order_by('-year')
    
    context = {
        'documents': documents,
        'search_query': search_query,
        'document_types': document_types,
        'letters': letters,
        'selected_type': selected_type,
        'selected_letter': selected_letter,
        'selected_year': selected_year,
        'years': years,
    }
    return render(request, 'documents/document_list.html', context)

def document_view(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if not document.pdf_file:
        return render(request, 'documents/document_view.html', {'document': document, 'error': 'No PDF available.'})
    return render(request, 'documents/document_view.html', {'document': document})