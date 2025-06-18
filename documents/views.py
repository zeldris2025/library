from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import os
from .models import Document
from calendar import month_name

def document_list(request):
    documents = Document.objects.all()
    search_query = request.GET.get('q', '')
    selected_type = request.GET.get('type', '')
    selected_letter = request.GET.get('letter', '')
    selected_year = request.GET.get('year', '')
    selected_month = request.GET.get('month', '')
    selected_day = request.GET.get('day', '')
    
    if search_query:
        documents = documents.filter(title__icontains=search_query) | documents.filter(content__icontains=search_query)
    
    if selected_type:
        documents = documents.filter(document_type=selected_type)
    if selected_letter:
        documents = documents.filter(title__istartswith=selected_letter)
    if selected_year:
        try:
            selected_year = int(selected_year)
            documents = documents.filter(date__year=selected_year)
        except ValueError:
            pass
    if selected_month:
        try:
            selected_month = int(selected_month)
            documents = documents.filter(date__month=selected_month)
        except ValueError:
            selected_month = ''
    if selected_day and selected_month:
        try:
            selected_day = int(selected_day)
            documents = documents.filter(date__day=selected_day)
        except ValueError:
            selected_day = ''
    
    paginator = Paginator(documents, 20)
    page = request.GET.get('page')
    try:
        documents = paginator.page(page)
    except PageNotAnInteger:
        documents = paginator.page(1)
    except EmptyPage:
        documents = paginator.page(paginator.num_pages)
    
    document_types = Document.DOCUMENT_TYPES
    letters = [chr(i) for i in range(65, 91)]
    years = Document.objects.values_list('date__year', flat=True).distinct().order_by('-date__year').filter(date__year__isnull=False)
    
    months = [{'number': i, 'name': month_name[i]} for i in range(1, 13)]
    days = []
    if selected_month and selected_year:
        try:
            from calendar import monthrange
            _, last_day = monthrange(int(selected_year), int(selected_month))
            days = [str(i) for i in range(1, last_day + 1)]
        except ValueError:
            pass
    
    context = {
        'documents': documents,
        'search_query': search_query,
        'document_types': document_types,
        'letters': letters,
        'selected_type': selected_type,
        'selected_letter': selected_letter,
        'selected_year': selected_year,
        'years': years,
        'selected_month': selected_month,
        'months': months,
        'selected_day': selected_day,
        'days': days,
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
    if document.pdf_file:
        try:
            if not os.path.exists(document.pdf_file.path):
                context['error'] = 'PDF file not found on server.'
        except OSError:
            context['error'] = 'Error accessing PDF file.'
    return render(request, 'documents/document_view.html', context)