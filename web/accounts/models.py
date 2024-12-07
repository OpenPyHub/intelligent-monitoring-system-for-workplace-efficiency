from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    affiliation = models.CharField(max_length=50, blank=False, null=True)

    def __str__(self):
        return self.username
