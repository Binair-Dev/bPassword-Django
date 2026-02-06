from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import JSONParser

from .models import APIKey
from django.contrib.auth.models import User
from passwords.models import Credentials # Import Credentials model
from passwords.encryption import password_encryption # Import encryption utility
from django.db.models import Q # For OR queries
from .rate_limiter import APIRateLimiter
from accounts.audit import log_credential_search, log_credential_access, log_credential_create, log_credential_update, log_credential_delete, get_client_ip
from .serializers import CredentialSerializer

import logging
import re

logger = logging.getLogger('security')


class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('Authorization')
        if not api_key:
            return None
        
        # Expecting 'Api-Key <your_key>'
        if not api_key.startswith('Api-Key '):
            raise AuthenticationFailed('Invalid API key header format. Expected "Api-Key <your_key>".')
        
        key = api_key.split(' ')[1]
        
        try:
            api_key_obj = APIKey.objects.select_related('user').get(key=key)
            # Log successful API key usage
            logger.info(f"API Key {key} used successfully by user: {api_key_obj.user.username} from IP: {request.META.get('REMOTE_ADDR')}")
            return (api_key_obj.user, None) # (user, auth)
        except APIKey.DoesNotExist:
            logger.warning(f"Invalid API Key attempt: {key} from IP: {request.META.get('REMOTE_ADDR')}")
            raise AuthenticationFailed('Invalid API Key.')

class CredentialSearchView(APIView):
    authentication_classes = [APIKeyAuthentication]

    def get(self, request, format=None):
        # Ensure user is authenticated by APIKeyAuthentication
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        # Check rate limiting
        is_allowed, remaining_minute, remaining_hour = APIRateLimiter.check_rate_limit(request)
        if not is_allowed:
            remaining_time = APIRateLimiter.get_lockout_remaining_time(request)
            if remaining_time:
                seconds = int(remaining_time.total_seconds())
                logger.warning(
                    f"API rate limit blocked for user {request.user.username} (ID: {request.user.id}) "
                    f"from IP {request.META.get('REMOTE_ADDR')}. "
                    f"Wait {seconds} seconds"
                )
                return Response(
                    {"detail": f"Rate limit exceeded. Please wait {seconds} seconds."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        query = request.query_params.get('q', None)

        if not query:
            return Response({"detail": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Filter credentials for the authenticated user
        # Perform case-insensitive search on 'name' field
        credentials = Credentials.objects.filter(
            Q(user=request.user) &
            Q(name__icontains=query)
        )

        results = []
        credential_ids = []
        for cred in credentials:
            credential_ids.append(cred.id)
            try:
                decrypted_password = password_encryption.decrypt(cred.password)
            except Exception as e:
                logger.error(f"Error decrypting password for credential ID {cred.id}: {e}")
                decrypted_password = "[DECRYPTION_ERROR]" # Indicate decryption failure

            results.append({
                "id": cred.id,
                "name": cred.name,
                "username": cred.username,
                "password": decrypted_password,
            })

        # Log the search and credential access (no sensitive data in logs)
        log_credential_search(
            user=request.user,
            query=query,
            ip_address=get_client_ip(request),
            results_count=len(credentials)
        )

        if credential_ids:
            log_credential_access(
                user=request.user,
                credential_ids=credential_ids,
                ip_address=get_client_ip(request),
                action='api_search'
            )

        return Response(results, status=status.HTTP_200_OK)


# ==================== Validation Functions ====================

def _validate_credential_input(name, username, password):
    """
    Valide les données d'entrée pour les credentials (API)
    """
    errors = []

    # Validation des longueurs
    if len(name) > 255:
        errors.append("Le nom ne peut pas dépasser 255 caractères.")
    if len(username) > 255:
        errors.append("Le nom d'utilisateur ne peut pas dépasser 255 caractères.")
    if len(password) > 1000:  # Limite raisonnable avant chiffrement
        errors.append("Le mot de passe est trop long.")

    # Validation des caractères dangereux
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
    for char in dangerous_chars:
        if char in name or char in username:
            errors.append("Caractères non autorisés détectés.")
            break

    # Validation avec regex pour éviter les injections
    if not re.match(r'^[a-zA-Z0-9\s\-_\.@]+$', name) and name:
        errors.append("Le nom contient des caractères non autorisés.")
    if not re.match(r'^[a-zA-Z0-9\s\-_\.@]+$', username) and username:
        errors.append("Le nom d'utilisateur contient des caractères non autorisés.")

    return errors


def _check_password_strength(password):
    """
    Vérifie la force d'un mot de passe et retourne True si faible
    """
    if len(password) < 12:
        return True
    if not re.search(r'[A-Z]', password):
        return True
    if not re.search(r'[a-z]', password):
        return True
    if not re.search(r'[0-9]', password):
        return True
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return True
    return False


# ==================== CRUD Views ====================

class CredentialListView(ListCreateAPIView):
    """
    List all credentials or create a new credential.
    GET /api/credentials/ - List all user's credentials
    POST /api/credentials/ - Create a new credential
    """
    authentication_classes = [APIKeyAuthentication]
    serializer_class = CredentialSerializer

    def get_queryset(self):
        """Filter credentials for the authenticated user"""
        return Credentials.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        GET - List all credentials (with optional search via ?q=query)
        """
        # Check rate limiting
        is_allowed, remaining_minute, remaining_hour = APIRateLimiter.check_rate_limit(request)
        if not is_allowed:
            remaining_time = APIRateLimiter.get_lockout_remaining_time(request)
            if remaining_time:
                seconds = int(remaining_time.total_seconds())
                logger.warning(
                    f"API rate limit blocked for user {request.user.username} (ID: {request.user.id}) "
                    f"from IP {request.META.get('REMOTE_ADDR')}. "
                    f"Wait {seconds} seconds"
                )
                return Response(
                    {"detail": f"Rate limit exceeded. Please wait {seconds} seconds."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        # Check for search query parameter
        query = request.query_params.get('q', None)

        if query:
            # Perform search
            credentials = Credentials.objects.filter(
                user=request.user,
                name__icontains=query
            )

            # Log the search
            log_credential_search(
                user=request.user,
                query=query,
                ip_address=get_client_ip(request),
                results_count=credentials.count()
            )
        else:
            # Return all credentials
            credentials = self.get_queryset()

        credential_ids = [cred.id for cred in credentials]

        results = []
        for cred in credentials:
            try:
                decrypted_password = cred.get_decrypted_password()
            except Exception as e:
                logger.error(f"Error decrypting password for credential ID {cred.id}: {e}")
                decrypted_password = "[DECRYPTION_ERROR]"

            results.append({
                "id": cred.id,
                "name": cred.name,
                "username": cred.username,
                "password": decrypted_password,
            })

        # Log the credential access
        log_credential_access(
            user=request.user,
            credential_ids=credential_ids,
            ip_address=get_client_ip(request),
            action='api_list' if not query else 'api_search'
        )

        return Response(results, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        POST - Create a new credential
        """
        # Check rate limiting
        is_allowed, remaining_minute, remaining_hour = APIRateLimiter.check_rate_limit(request)
        if not is_allowed:
            remaining_time = APIRateLimiter.get_lockout_remaining_time(request)
            if remaining_time:
                seconds = int(remaining_time.total_seconds())
                logger.warning(
                    f"API rate limit blocked for user {request.user.username} (ID: {request.user.id}) "
                    f"from IP {request.META.get('REMOTE_ADDR')}. "
                    f"Wait {seconds} seconds"
                )
                return Response(
                    {"detail": f"Rate limit exceeded. Please wait {seconds} seconds."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        # Parse request data
        data = JSONParser().parse(request)
        name = data.get('name', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        # Validation de base
        if not all([name, username, password]):
            return Response(
                {"detail": "Tous les champs (name, username, password) sont obligatoires."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validation avancée
        validation_errors = _validate_credential_input(name, username, password)
        if validation_errors:
            return Response(
                {"detail": "Validation error", "errors": validation_errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier les doublons
        if Credentials.objects.filter(user=request.user, name=name, username=username).exists():
            return Response(
                {"detail": "Un identifiant avec ce nom et nom d'utilisateur existe déjà."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Avertissement si mot de passe faible (sans bloquer)
        password_weak = _check_password_strength(password)
        if password_weak:
            logger.warning(
                f"User {request.user.username} created a weak password credential '{name}'"
            )

        # Create credential (encryption handled by model save)
        credential = Credentials.objects.create(
            user=request.user,
            name=name,
            username=username,
            password=password  # Will be encrypted by model save()
        )

        # Log la création
        log_credential_create(
            user=request.user,
            name=name,
            ip_address=get_client_ip(request)
        )

        # Return created credential with decrypted password
        try:
            decrypted_password = credential.get_decrypted_password()
        except Exception as e:
            logger.error(f"Error decrypting password for credential ID {credential.id}: {e}")
            decrypted_password = "[DECRYPTION_ERROR]"

        response_data = {
            "id": credential.id,
            "name": credential.name,
            "username": credential.username,
            "password": decrypted_password,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class CredentialDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a credential instance.
    GET /api/credentials/<id>/ - Get a specific credential
    PUT /api/credentials/<id>/ - Update a credential (full)
    PATCH /api/credentials/<id>/ - Update a credential (partial)
    DELETE /api/credentials/<id>/ - Delete a credential
    """
    authentication_classes = [APIKeyAuthentication]
    serializer_class = CredentialSerializer

    def get_queryset(self):
        """Filter credentials for the authenticated user"""
        return Credentials.objects.filter(user=self.request.user)

    def get_object(self):
        """
        Get credential object and verify ownership
        """
        queryset = self.get_queryset()
        obj = queryset.filter(pk=self.kwargs['pk']).first()
        if not obj:
            raise Exception("Credential not found")
        return obj

    def retrieve(self, request, *args, **kwargs):
        """
        GET - Get a specific credential by ID
        """
        # Check rate limiting
        is_allowed, remaining_minute, remaining_hour = APIRateLimiter.check_rate_limit(request)
        if not is_allowed:
            remaining_time = APIRateLimiter.get_lockout_remaining_time(request)
            if remaining_time:
                seconds = int(remaining_time.total_seconds())
                logger.warning(
                    f"API rate limit blocked for user {request.user.username} (ID: {request.user.id}) "
                    f"from IP {request.META.get('REMOTE_ADDR')}. "
                    f"Wait {seconds} seconds"
                )
                return Response(
                    {"detail": f"Rate limit exceeded. Please wait {seconds} seconds."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        try:
            credential = self.get_object()
        except Exception:
            return Response(
                {"detail": "Credential not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Decrypt password
        try:
            decrypted_password = credential.get_decrypted_password()
        except Exception as e:
            logger.error(f"Error decrypting password for credential ID {credential.id}: {e}")
            decrypted_password = "[DECRYPTION_ERROR]"

        response_data = {
            "id": credential.id,
            "name": credential.name,
            "username": credential.username,
            "password": decrypted_password,
        }

        # Log credential access
        log_credential_access(
            user=request.user,
            credential_ids=[credential.id],
            ip_address=get_client_ip(request),
            action='api_retrieve'
        )

        return Response(response_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        PUT/PATCH - Update a credential
        """
        # Check rate limiting
        is_allowed, remaining_minute, remaining_hour = APIRateLimiter.check_rate_limit(request)
        if not is_allowed:
            remaining_time = APIRateLimiter.get_lockout_remaining_time(request)
            if remaining_time:
                seconds = int(remaining_time.total_seconds())
                logger.warning(
                    f"API rate limit blocked for user {request.user.username} (ID: {request.user.id}) "
                    f"from IP {request.META.get('REMOTE_ADDR')}. "
                    f"Wait {seconds} seconds"
                )
                return Response(
                    {"detail": f"Rate limit exceeded. Please wait {seconds} seconds."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        try:
            credential = self.get_object()
        except Exception:
            return Response(
                {"detail": "Credential not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Parse request data
        data = JSONParser().parse(request)
        name = data.get('name', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        # Validation de base
        if not all([name, username, password]):
            return Response(
                {"detail": "Tous les champs (name, username, password) sont obligatoires."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validation avancée
        validation_errors = _validate_credential_input(name, username, password)
        if validation_errors:
            return Response(
                {"detail": "Validation error", "errors": validation_errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier les doublons (sauf pour l'enregistrement actuel)
        duplicate = Credentials.objects.filter(
            user=request.user,
            name=name,
            username=username
        ).exclude(id=credential.id).exists()

        if duplicate:
            return Response(
                {"detail": "Un identifiant avec ce nom et nom d'utilisateur existe déjà."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Avertissement si mot de passe faible (sans bloquer)
        password_weak = _check_password_strength(password)
        if password_weak:
            logger.warning(
                f"User {request.user.username} updated credential '{name}' with a weak password"
            )

        # Update credential (encryption handled by model save)
        credential.name = name
        credential.username = username
        credential.password = password  # Will be encrypted by model save()
        credential.save()

        # Log la modification
        log_credential_update(
            user=request.user,
            credential_id=credential.id,
            name=name,
            ip_address=get_client_ip(request)
        )

        # Return updated credential with decrypted password
        try:
            decrypted_password = credential.get_decrypted_password()
        except Exception as e:
            logger.error(f"Error decrypting password for credential ID {credential.id}: {e}")
            decrypted_password = "[DECRYPTION_ERROR]"

        response_data = {
            "id": credential.id,
            "name": credential.name,
            "username": credential.username,
            "password": decrypted_password,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE - Delete a credential
        """
        # Check rate limiting
        is_allowed, remaining_minute, remaining_hour = APIRateLimiter.check_rate_limit(request)
        if not is_allowed:
            remaining_time = APIRateLimiter.get_lockout_remaining_time(request)
            if remaining_time:
                seconds = int(remaining_time.total_seconds())
                logger.warning(
                    f"API rate limit blocked for user {request.user.username} (ID: {request.user.id}) "
                    f"from IP {request.META.get('REMOTE_ADDR')}. "
                    f"Wait {seconds} seconds"
                )
                return Response(
                    {"detail": f"Rate limit exceeded. Please wait {seconds} seconds."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        try:
            credential = self.get_object()
        except Exception:
            return Response(
                {"detail": "Credential not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        name = credential.name
        credential_id = credential.id

        # Delete credential
        credential.delete()

        # Log la suppression
        log_credential_delete(
            user=request.user,
            credential_id=credential_id,
            name=name,
            ip_address=get_client_ip(request)
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
