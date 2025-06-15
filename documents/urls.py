from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.document_list, name='document_list'),
    path('<int:pk>/view/', views.document_view, name='document_view'),
]