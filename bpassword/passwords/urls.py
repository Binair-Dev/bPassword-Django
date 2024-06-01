from django.contrib import admin
from django.urls import include, path
from .views import delete, passwords, update

urlpatterns = [
    path('', passwords, name='passwords'),
    path('update/<int:id>/', update, name='update'),
    path('delete/<int:id>/', delete, name='delete'),
]
