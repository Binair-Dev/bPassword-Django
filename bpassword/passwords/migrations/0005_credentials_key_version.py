# Generated for bPassword security enhancement

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passwords', '0004_alter_credentials_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='credentials',
            name='key_version',
            field=models.IntegerField(default=1),
        ),
    ]
