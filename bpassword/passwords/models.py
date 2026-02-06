from django.db import models
from django.contrib.auth.models import User
from .encryption import password_encryption

class Credentials(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=255, default="")
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=500)  # Augmenté pour le chiffrement
    key_version = models.IntegerField(default=1)  # Version de clé de chiffrement

    def save(self, *args, **kwargs):
        # Chiffrer le mot de passe avant sauvegarde
        if self.password and not self.password.startswith('gAAAAA'):  # Éviter double chiffrement
            self.password = password_encryption.encrypt(self.password, self.key_version)
        super().save(*args, **kwargs)

    def get_decrypted_password(self):
        """
        Retourne le mot de passe déchiffré
        Effectue automatiquement le rekeying si la clé a changé
        """
        # Déchiffrer avec la version actuelle
        password = password_encryption.decrypt(self.password, self.key_version)

        # Rekeying automatique si nécessaire
        from passwords.encryption import CURRENT_KEY_VERSION
        if self.key_version != CURRENT_KEY_VERSION:
            try:
                # Re-chiffrer avec la nouvelle version
                self.password = password_encryption.encrypt(password, CURRENT_KEY_VERSION)
                self.key_version = CURRENT_KEY_VERSION

                # Sauvegarder seulement la version (pas ré-chiffrer à nouveau)
                super().save(update_fields=['password', 'key_version'])

                # Logger le rekeying
                import logging
                logger = logging.getLogger('security')
                logger.info(
                    f"Auto-rekeying: credential ID {self.id} for user {self.user.username} "
                    f"from version {self.key_version} to version {CURRENT_KEY_VERSION}"
                )
            except Exception as e:
                # Logger l'erreur mais ne pas bloquer l'accès
                import logging
                logger = logging.getLogger('security')
                logger.error(f"Failed to auto-rekey credential ID {self.id}: {e}")

        return password
    
    class Meta:
        verbose_name = "Credential"
        verbose_name_plural = "Credentials"