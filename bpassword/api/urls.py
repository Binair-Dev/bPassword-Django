from django.urls import path
from .views import CredentialSearchView, CredentialListView, CredentialDetailView

urlpatterns = [
    # CRUD endpoints - Support both with and without trailing slash
    path('credentials', CredentialListView.as_view(), name='credential-list'),  # List & Create (no slash)
    path('credentials/', CredentialListView.as_view(), name='credential-list-slash'),  # List & Create (with slash)
    path('credentials/<int:pk>', CredentialDetailView.as_view(), name='credential-detail'),  # Read, Update, Delete (no slash)
    path('credentials/<int:pk>/', CredentialDetailView.as_view(), name='credential-detail-slash'),  # Read, Update, Delete (with slash)
    # Legacy search endpoint (for backward compatibility - use /api/credentials/?q= instead)
    path('credentials/search', CredentialSearchView.as_view(), name='credential_search'),
]
