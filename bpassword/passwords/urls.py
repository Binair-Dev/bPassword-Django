from django.contrib import admin
from django.urls import include, path
from .views import delete, passwords, update, export_credentials, import_credentials

urlpatterns = [
    path('', passwords, name='passwords'),
    path('update/<int:id>/', update, name='update'),
    path('delete/<int:id>/', delete, name='delete'),
    path('export/', export_credentials, name='export_credentials'),
    path('import/', import_credentials, name='import_credentials'),
]
