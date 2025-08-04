from django.db import models
from django.contrib.auth.models import User
from .encryption import password_encryption

class Credentials(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=255, default="")
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=500)  # Augmenté pour le chiffrement
    
    def save(self, *args, **kwargs):
        # Chiffrer le mot de passe avant sauvegarde
        if self.password and not self.password.startswith('gAAAAA'):  # Éviter double chiffrement
            self.password = password_encryption.encrypt(self.password)
        super().save(*args, **kwargs)
    
    def get_decrypted_password(self):
        """Retourne le mot de passe déchiffré"""
        return password_encryption.decrypt(self.password)
    
    class Meta:
        verbose_name = "Credential"
        verbose_name_plural = "Credentials"