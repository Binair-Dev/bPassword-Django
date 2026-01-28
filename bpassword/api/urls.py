from django.urls import path
from .views import CredentialSearchView

urlpatterns = [
    path('credentials/', CredentialSearchView.as_view(), name='credential_search'),
]
