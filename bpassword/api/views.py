from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import APIKey
from django.contrib.auth.models import User
from passwords.models import Credentials # Import Credentials model
from passwords.encryption import password_encryption # Import encryption utility
from django.db.models import Q # For OR queries
from .rate_limiter import APIRateLimiter
from accounts.audit import log_credential_search, log_credential_access, get_client_ip

import logging

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
