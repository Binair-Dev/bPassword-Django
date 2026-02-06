from django.core.exceptions import ValidationError
import re

class PasswordComplexityValidator:
    """Validateur de complexité de mot de passe pour la création de compte"""

    def validate(self, password, user=None):
        """
        Valide que le mot de passe respecte les exigences de complexité:
        - Au moins 12 caractères
        - Au moins une majuscule
        - Au moins une minuscule
        - Au moins un chiffre
        - Au moins un caractère spécial
        """
        if len(password) < 12:
            raise ValidationError(
                "Le mot de passe doit contenir au moins 12 caractères.",
                code='password_too_short',
            )

        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une majuscule.",
                code='password_no_uppercase',
            )

        if not re.search(r'[a-z]', password):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une minuscule.",
                code='password_no_lowercase',
            )

        if not re.search(r'[0-9]', password):
            raise ValidationError(
                "Le mot de passe doit contenir au moins un chiffre.",
                code='password_no_digit',
            )

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                "Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&*(),.?\":{}|<>).",
                code='password_no_special',
            )

    def get_help_text(self):
        return "Votre mot de passe doit contenir au moins 12 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial."
