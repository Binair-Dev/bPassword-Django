from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
import base64
import os
import hashlib
import logging

logger = logging.getLogger('security')

# Version actuelle de la clé de chiffrement
CURRENT_KEY_VERSION = 1

# Configuration des clés (peut être étendue pour supporter plusieurs versions)
# Par défaut, toutes les versions utilisent SECRET_KEY comme base
# Pour une vraie rotation, il faudrait configurer des clés différentes par version
KEY_VERSIONS = {
    1: settings.SECRET_KEY.encode(),
    # Pour ajouter une nouvelle clé:
    # 2: 'nouvelle_clé_différente'.encode(),
}

class PasswordEncryption:
    def __init__(self):
        # Utiliser la clé de la version actuelle comme master key
        self.master_key = KEY_VERSIONS.get(CURRENT_KEY_VERSION, settings.SECRET_KEY.encode())

    def _derive_key(self, salt, key_version=None):
        """Dérive une clé unique basée sur un salt et une version de clé"""
        # Si key_version n'est pas spécifié, utiliser la version actuelle
        if key_version is None:
            key_version = CURRENT_KEY_VERSION

        # Récupérer la clé de base pour cette version
        base_key = KEY_VERSIONS.get(key_version, self.master_key)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # Nombre d'itérations élevé pour la sécurité
        )
        key = kdf.derive(base_key)
        return base64.urlsafe_b64encode(key)

    def encrypt(self, password, key_version=None):
        """Chiffre un mot de passe avec un salt unique"""
        if not password:
            return ""

        # Si key_version n'est pas spécifié, utiliser la version actuelle
        if key_version is None:
            key_version = CURRENT_KEY_VERSION

        # Générer un salt aléatoire unique
        salt = os.urandom(16)

        # Dériver une clé unique basée sur ce salt
        key = self._derive_key(salt, key_version)
        cipher = Fernet(key)

        # Chiffrer le mot de passe
        encrypted = cipher.encrypt(password.encode())

        # Combiner salt + données chiffrées et encoder en base64
        combined = salt + encrypted
        return base64.urlsafe_b64encode(combined).decode()

    def decrypt(self, encrypted_password, key_version=None):
        """Déchiffre un mot de passe"""
        if not encrypted_password:
            return ""

        try:
            # Décoder le format base64
            combined = base64.urlsafe_b64decode(encrypted_password.encode())

            # Extraire le salt (16 premiers bytes)
            salt = combined[:16]
            encrypted_data = combined[16:]

            # Dériver la clé avec la version spécifiée
            key = self._derive_key(salt, key_version)
            cipher = Fernet(key)

            # Déchiffrer
            return cipher.decrypt(encrypted_data).decode()

        except Exception as e:
            # Compatibilité avec l'ancien système (sans version de clé)
            try:
                # Tenter l'ancien format (sans salt)
                old_key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
                old_cipher = Fernet(base64.urlsafe_b64encode(old_key))
                return old_cipher.decrypt(encrypted_password.encode()).decode()
            except Exception as e2:
                # Si tout échoue, logger l'erreur
                logger.error(f"Failed to decrypt password with key_version {key_version}: {e2}")
                return encrypted_password

# Instance globale
password_encryption = PasswordEncryption()