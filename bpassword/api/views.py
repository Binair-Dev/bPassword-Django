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
        for cred in credentials:
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
        
        return Response(results, status=status.HTTP_200_OK)
