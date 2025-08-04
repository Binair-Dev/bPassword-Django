# Generated manually for adding user field to Credentials model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('passwords', '0002_credentials_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='credentials',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='credentials',
            name='password',
            field=models.CharField(max_length=500),
        ),
    ]