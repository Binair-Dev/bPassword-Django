from django.core.management.base import BaseCommand, CommandError
from passwords.models import Credentials
from passwords.encryption import password_encryption, CURRENT_KEY_VERSION
from django.db import transaction
import logging

logger = logging.getLogger('security')


class Command(BaseCommand):
    help = 'Re-key all encrypted passwords to a new encryption key version'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to-version',
            type=int,
            required=True,
            help='Target key version to re-encrypt passwords to',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually changing anything',
        )

    def handle(self, *args, **options):
        target_version = options['to_version']
        dry_run = options['dry_run']

        self.stdout.write(self.style.NOTICE(f'Starting password re-keying to version {target_version}'))

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        # Trouver tous les identifiants
        credentials = Credentials.objects.all()

        if not credentials.exists():
            self.stdout.write(self.style.WARNING('No credentials found in database'))
            return

        total_count = credentials.count()
        already_on_target = credentials.filter(key_version=target_version).count()
        needs_rekeying = credentials.filter(key_version__lt=target_version)

        self.stdout.write(f'Total credentials: {total_count}')
        self.stdout.write(f'Already on target version {target_version}: {already_on_target}')
        self.stdout.write(f'Credentials to re-key: {needs_rekeying.count()}')

        if needs_rekeying.count() == 0:
            self.stdout.write(self.style.SUCCESS('All credentials are already on the target version'))
            return

        # Confirmation si pas dry-run
        if not dry_run:
            confirm = input(
                f'\nThis will re-key {needs_rekeying.count()} credentials to version {target_version}. '
                f'Are you sure? Type "yes" to continue: '
            )
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Aborted'))
                return

        # Re-keying
        success_count = 0
        error_count = 0

        for cred in needs_rekeying:
            try:
                # Déchiffrer avec l'ancienne version
                current_password = password_encryption.decrypt(cred.password, cred.key_version)

                if dry_run:
                    self.stdout.write(
                        f'[DRY RUN] Would re-key credential ID {cred.id} '
                        f'({cred.name}) from version {cred.key_version} to {target_version}'
                    )
                    success_count += 1
                else:
                    # Re-chiffrer avec la nouvelle version
                    with transaction.atomic():
                        cred.password = password_encryption.encrypt(current_password, target_version)
                        cred.key_version = target_version
                        cred.save(update_fields=['password', 'key_version'])

                        # Logger
                        logger.info(
                            f"Manual re-keying: credential ID {cred.id} "
                            f"for user {cred.user.username} from version {cred.key_version} "
                            f"to version {target_version}"
                        )

                        self.stdout.write(
                            f'Re-keyed credential ID {cred.id} ({cred.name}) '
                            f'from version {cred.key_version} to {target_version}'
                        )
                        success_count += 1

            except Exception as e:
                error_count += 1
                logger.error(
                    f"Failed to re-key credential ID {cred.id}: {e}"
                )
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to re-key credential ID {cred.id}: {str(e)}'
                    )
                )

        # Résumé
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('Re-keying Summary:')
        self.stdout.write(f'  Total processed: {needs_rekeying.count()}')
        self.stdout.write(f'  Successful: {self.style.SUCCESS(str(success_count))}')
        self.stdout.write(f'  Failed: {self.style.ERROR(str(error_count))}')
        self.stdout.write('=' * 60)

        if not dry_run and error_count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully re-keyed {success_count} credentials to version {target_version}'
                )
            )
        elif not dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\nCompleted with {error_count} errors. Check the security logs for details.'
                )
            )
