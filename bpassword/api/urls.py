from django.urls import path
from .views import CredentialSearchView, CredentialListView, CredentialDetailView

urlpatterns = [
    # CRUD endpoints (recommended)
    path('credentials/', CredentialListView.as_view(), name='credential-list'),  # List & Create
    path('credentials/<int:pk>/', CredentialDetailView.as_view(), name='credential-detail'),  # Read, Update, Delete
    # Legacy search endpoint (for backward compatibility - use /api/credentials/?q= instead)
    path('credentials/search/', CredentialSearchView.as_view(), name='credential_search'),
]
