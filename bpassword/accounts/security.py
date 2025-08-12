from django.core.cache import cache
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import hashlib

class LoginSecurityManager:
    """Gestionnaire de sécurité pour les tentatives de connexion"""
    
    # Configuration
    MAX_LOGIN_ATTEMPTS = 3
    LOCKOUT_DURATION = timedelta(hours=1)  # 1 heure de blocage
    
    @classmethod
    def _get_cache_key(cls, identifier):
        """Génère une clé de cache unique pour l'identifiant"""
        # Utiliser un hash pour éviter l'exposition des IPs
        hashed = hashlib.sha256(identifier.encode()).hexdigest()
        return f"login_attempts_{hashed}"
    
    @classmethod
    def _get_lockout_key(cls, identifier):
        """Génère une clé de cache pour le verrouillage"""
        hashed = hashlib.sha256(identifier.encode()).hexdigest()
        return f"login_lockout_{hashed}"
    
    @classmethod
    def get_client_identifier(cls, request):
        """Obtient un identifiant unique pour le client"""
        # Combiner IP et User-Agent pour un identifiant plus robuste
        ip = cls._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:100]  # Limiter la taille
        return f"{ip}:{hashlib.md5(user_agent.encode()).hexdigest()[:10]}"
    
    @classmethod
    def _get_client_ip(cls, request):
        """Obtient l'IP réelle du client"""
        # Vérifier les headers de proxy
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip
    
    @classmethod
    def is_locked(cls, request):
        """Vérifie si le client est verrouillé"""
        identifier = cls.get_client_identifier(request)
        lockout_key = cls._get_lockout_key(identifier)
        
        lockout_time = cache.get(lockout_key)
        if lockout_time:
            if timezone.now() < lockout_time:
                return True
            else:
                # Le verrouillage a expiré, nettoyer
                cls.clear_attempts(request)
        
        return False
    
    @classmethod
    def get_lockout_remaining_time(cls, request):
        """Retourne le temps restant de verrouillage"""
        identifier = cls.get_client_identifier(request)
        lockout_key = cls._get_lockout_key(identifier)
        
        lockout_time = cache.get(lockout_key)
        if lockout_time and timezone.now() < lockout_time:
            remaining = lockout_time - timezone.now()
            return remaining
        
        return None
    
    @classmethod
    def record_failed_attempt(cls, request):
        """Enregistre une tentative de connexion échouée"""
        identifier = cls.get_client_identifier(request)
        attempts_key = cls._get_cache_key(identifier)
        lockout_key = cls._get_lockout_key(identifier)
        
        # Incrémenter le compteur de tentatives
        attempts = cache.get(attempts_key, 0) + 1
        cache.set(attempts_key, attempts, timeout=3600)  # Expire après 1 heure
        
        # Si le nombre max de tentatives est atteint, verrouiller
        if attempts >= cls.MAX_LOGIN_ATTEMPTS:
            lockout_until = timezone.now() + cls.LOCKOUT_DURATION
            cache.set(lockout_key, lockout_until, timeout=3600)  # 1 heure
            
            # Log de sécurité (optionnel)
            import logging
            logger = logging.getLogger('security')
            logger.warning(f"Login lockout activated for {cls._get_client_ip(request)} after {attempts} failed attempts")
        
        return attempts
    
    @classmethod
    def clear_attempts(cls, request):
        """Efface les tentatives enregistrées (après connexion réussie)"""
        identifier = cls.get_client_identifier(request)
        attempts_key = cls._get_cache_key(identifier)
        lockout_key = cls._get_lockout_key(identifier)
        
        cache.delete(attempts_key)
        cache.delete(lockout_key)
    
    @classmethod
    def get_remaining_attempts(cls, request):
        """Retourne le nombre de tentatives restantes"""
        identifier = cls.get_client_identifier(request)
        attempts_key = cls._get_cache_key(identifier)
        
        attempts = cache.get(attempts_key, 0)
        return max(0, cls.MAX_LOGIN_ATTEMPTS - attempts)