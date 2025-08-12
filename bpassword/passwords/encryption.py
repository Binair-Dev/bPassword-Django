from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
import base64
import os
import hashlib

class PasswordEncryption:
    def __init__(self):
        # Utiliser une clé de base solide
        self.master_key = settings.SECRET_KEY.encode()
    
    def _derive_key(self, salt):
        """Dérive une clé unique basée sur un salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # Nombre d'itérations élevé pour la sécurité
        )
        key = kdf.derive(self.master_key)
        return base64.urlsafe_b64encode(key)
    
    def encrypt(self, password):
        """Chiffre un mot de passe avec un salt unique"""
        if not password:
            return ""
        
        # Générer un salt aléatoire unique
        salt = os.urandom(16)
        
        # Dériver une clé unique basée sur ce salt
        key = self._derive_key(salt)
        cipher = Fernet(key)
        
        # Chiffrer le mot de passe
        encrypted = cipher.encrypt(password.encode())
        
        # Combiner salt + données chiffrées et encoder en base64
        combined = salt + encrypted
        return base64.urlsafe_b64encode(combined).decode()
    
    def decrypt(self, encrypted_password):
        """Déchiffre un mot de passe"""
        if not encrypted_password:
            return ""
        
        try:
            # Décoder le format base64
            combined = base64.urlsafe_b64decode(encrypted_password.encode())
            
            # Extraire le salt (16 premiers bytes)
            salt = combined[:16]
            encrypted_data = combined[16:]
            
            # Dériver la même clé avec le salt
            key = self._derive_key(salt)
            cipher = Fernet(key)
            
            # Déchiffrer
            return cipher.decrypt(encrypted_data).decode()
            
        except Exception:
            # Compatibilité avec l'ancien système
            try:
                # Tenter l'ancien format
                old_key = hashlib.sha256(self.master_key).digest()
                old_cipher = Fernet(base64.urlsafe_b64encode(old_key))
                return old_cipher.decrypt(encrypted_password.encode()).decode()
            except Exception:
                # Si tout échoue, retourner la valeur d'origine
                return encrypted_password

# Instance globale
password_encryption = PasswordEncryption()