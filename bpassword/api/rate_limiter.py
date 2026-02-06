from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import hashlib
import logging

logger = logging.getLogger('security')


class APIRateLimiter:
    """
    Rate limiter pour l'API
    - 60 requêtes par minute
    - 1000 requêtes par heure
    """

    # Limites
    MAX_REQUESTS_PER_MINUTE = 60
    MAX_REQUESTS_PER_HOUR = 1000

    # Durée de verrouillage
    LOCKOUT_DURATION = timedelta(minutes=5)

    @classmethod
    def _get_client_identifier(cls, request):
        """
        Génère un identifiant unique basé sur l'IP et l'User-Agent
        """
        ip = request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else 'anon'

        # Hash pour éviter de stocker les données brutes
        identifier_string = f"{ip}:{user_agent}:{user_id}"
        return hashlib.sha256(identifier_string.encode()).hexdigest()

    @classmethod
    def _get_minute_key(cls, client_identifier):
        """Clé de cache pour le compteur minute"""
        current_minute = timezone.now().replace(second=0, microsecond=0)
        return f"api_rate_limit_minute_{client_identifier}_{current_minute.isoformat()}"

    @classmethod
    def _get_hour_key(cls, client_identifier):
        """Clé de cache pour le compteur heure"""
        current_hour = timezone.now().replace(minute=0, second=0, microsecond=0)
        return f"api_rate_limit_hour_{client_identifier}_{current_hour.isoformat()}"

    @classmethod
    def _get_lockout_key(cls, client_identifier):
        """Clé de cache pour le verrouillage"""
        return f"api_rate_limit_lockout_{client_identifier}"

    @classmethod
    def is_locked(cls, request):
        """Vérifie si le client est verrouillé"""
        client_identifier = cls._get_client_identifier(request)
        lockout_key = cls._get_lockout_key(client_identifier)
        return cache.get(lockout_key) is not None

    @classmethod
    def get_lockout_remaining_time(cls, request):
        """Retourne le temps de verrouillage restant"""
        client_identifier = cls._get_client_identifier(request)
        lockout_key = cls._get_lockout_key(client_identifier)
        expiration = cache.get(lockout_key)
        if expiration:
            return expiration - timezone.now()
        return None

    @classmethod
    def check_rate_limit(cls, request):
        """
        Vérifie et enregistre une requête API
        Retourne: (is_allowed, remaining_requests_per_minute, remaining_requests_per_hour)
        """
        client_identifier = cls._get_client_identifier(request)

        # Vérifier si verrouillé
        if cls.is_locked(request):
            return False, 0, 0

        minute_key = cls._get_minute_key(client_identifier)
        hour_key = cls._get_hour_key(client_identifier)

        # Obtenir les compteurs actuels
        minute_count = cache.get(minute_key, 0)
        hour_count = cache.get(hour_key, 0)

        # Vérifier les limites
        minute_allowed = minute_count < cls.MAX_REQUESTS_PER_MINUTE
        hour_allowed = hour_count < cls.MAX_REQUESTS_PER_HOUR

        if minute_allowed and hour_allowed:
            # Incrémenter les compteurs
            cache.set(minute_key, minute_count + 1, 60)  # TTL 1 minute
            cache.set(hour_key, hour_count + 1, 3600)  # TTL 1 heure
            return True, cls.MAX_REQUESTS_PER_MINUTE - minute_count - 1, cls.MAX_REQUESTS_PER_HOUR - hour_count - 1

        # Limite dépassée - verrouiller et logger
        cls._lockout(client_identifier)

        # Logger l'événement
        logger.warning(
            f"API rate limit exceeded for user {request.user.username} (ID: {request.user.id}) "
            f"from IP {request.META.get('REMOTE_ADDR')}. "
            f"Minute count: {minute_count}, Hour count: {hour_count}"
        )

        return False, 0, 0

    @classmethod
    def _lockout(cls, client_identifier):
        """Verrouille le client pour la durée définie"""
        lockout_key = cls._get_lockout_key(client_identifier)
        expiration = timezone.now() + cls.LOCKOUT_DURATION
        cache.set(lockout_key, expiration, int(cls.LOCKOUT_DURATION.total_seconds()))

    @classmethod
    def record_api_access(cls, request, user, action='search'):
        """Enregistre l'accès à l'API pour logging"""
        logger.info(
            f"API access: {action} by user {user.username} (ID: {user.id}) "
            f"from IP {request.META.get('REMOTE_ADDR')}"
        )
