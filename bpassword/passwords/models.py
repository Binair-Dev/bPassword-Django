from django.db import models

class Credentials(models.Model):
    name = models.CharField(max_length=255, default="")
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)