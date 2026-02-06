from rest_framework import serializers
from passwords.models import Credentials


class CredentialSerializer(serializers.ModelSerializer):
    """
    Serializer for the Credentials model.
    Handles CRUD operations with automatic encryption/decryption.
    """
    password = serializers.CharField(write_only=False, required=True)

    class Meta:
        model = Credentials
        fields = ['id', 'name', 'username', 'password', 'key_version']
        read_only_fields = ['id', 'key_version']

    def to_representation(self, instance):
        """
        Override to include decrypted password in responses.
        """
        data = super().to_representation(instance)
        # Decrypt password for GET requests
        try:
            data['password'] = instance.get_decrypted_password()
        except Exception as e:
            data['password'] = '[DECRYPTION_ERROR]'
        return data
