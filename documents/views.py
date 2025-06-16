from django.shortcuts import render, get_object_or_404
from .models import Document
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def document_list(request):
    documents = Document.objects.all()
    search_query = request.GET.get('q', '')
    selected_type = request.GET.get('type', '')
    selected_letter = request.GET.get('letter', '')
    selected_year = request.GET.get('year', '')
    
    if search_query:
        documents = documents.filter(title__icontains=search_query) | documents.filter(content__icontains=search_query)
    
    if selected_type:
        documents = documents.filter(document_type=selected_type)
    if selected_letter:
        documents = documents.filter(title__istartswith=selected_letter)
    if selected_year:
        try:
            selected_year = int(selected_year)  # Convert to int, no lstrip
            documents = documents.filter(year=selected_year)
        except ValueError:
            pass  # Ignore invalid years
    
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
    context = {
        'document': document,
        'search_query': request.GET.get('q', ''),
        'document_types': Document.DOCUMENT_TYPES,
        'selected_type': request.GET.get('type', ''),
    }
    return render(request, 'documents/document_view.html', context)