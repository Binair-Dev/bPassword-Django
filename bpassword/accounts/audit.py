import logging

logger = logging.getLogger('security')


def log_credential_access(user, credential_ids, ip_address, action='access'):
    """
    Enregistre l'accès aux identifiants

    Args:
        user: Utilisateur Django
        credential_ids: Liste des IDs des identifiants accédés (pas de données sensibles)
        ip_address: Adresse IP du client
        action: Type d'action (list, view, search, update, delete)
    """
    if credential_ids:
        ids_str = ', '.join(map(str, credential_ids))
    else:
        ids_str = 'None'

    logger.info(
        f"Credential access: {action} by user {user.username} (ID: {user.id}) "
        f"from IP {ip_address}. "
        f"Credentials accessed: {ids_str}"
    )


def log_credential_search(user, query, ip_address, results_count):
    """
    Enregistre une recherche d'identifiants

    Args:
        user: Utilisateur Django
        query: Terme de recherche
        ip_address: Adresse IP du client
        results_count: Nombre de résultats trouvés
    """
    logger.info(
        f"Credential search by user {user.username} (ID: {user.id}) "
        f"from IP {ip_address}. "
        f"Query: '{query}'. "
        f"Results: {results_count}"
    )


def log_credential_create(user, name, ip_address):
    """
    Enregistre la création d'un identifiant

    Args:
        user: Utilisateur Django
        name: Nom de l'identifiant
        ip_address: Adresse IP du client
    """
    logger.info(
        f"Credential created by user {user.username} (ID: {user.id}) "
        f"from IP {ip_address}. "
        f"Credential name: '{name}'"
    )


def log_credential_update(user, credential_id, name, ip_address):
    """
    Enregistre la modification d'un identifiant

    Args:
        user: Utilisateur Django
        credential_id: ID de l'identifiant modifié
        name: Nom de l'identifiant
        ip_address: Adresse IP du client
    """
    logger.info(
        f"Credential updated by user {user.username} (ID: {user.id}) "
        f"from IP {ip_address}. "
        f"Credential ID: {credential_id}, name: '{name}'"
    )


def log_credential_delete(user, credential_id, name, ip_address):
    """
    Enregistre la suppression d'un identifiant

    Args:
        user: Utilisateur Django
        credential_id: ID de l'identifiant supprimé
        name: Nom de l'identifiant
        ip_address: Adresse IP du client
    """
    logger.info(
        f"Credential deleted by user {user.username} (ID: {user.id}) "
        f"from IP {ip_address}. "
        f"Credential ID: {credential_id}, name: '{name}'"
    )


def get_client_ip(request):
    """
    Récupère l'adresse IP du client (gère les proxies)
    """
    # Vérifier d'abord les headers X-Forwarded-For (pour les proxies)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
