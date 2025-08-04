from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib

class PasswordEncryption:
    def __init__(self):
        # Générer une clé basée sur la SECRET_KEY de Django
        key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        # Fernet nécessite une clé de 32 bytes encodée en base64
        self.cipher = Fernet(base64.urlsafe_b64encode(key))
    
    def encrypt(self, password):
        """Chiffre un mot de passe"""
        if not password:
            return ""
        return self.cipher.encrypt(password.encode()).decode()
    
    def decrypt(self, encrypted_password):
        """Déchiffre un mot de passe"""
        if not encrypted_password:
            return ""
        try:
            return self.cipher.decrypt(encrypted_password.encode()).decode()
        except Exception:
            # Si le déchiffrement échoue, retourner la valeur d'origine
            # (pour la compatibilité avec les anciens mots de passe non chiffrés)
            return encrypted_password

# Instance globale
password_encryption = PasswordEncryption()