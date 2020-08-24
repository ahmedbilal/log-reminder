from django.db import models


class CommunicationMedium(models.TextChoices):
    EMAIL = "EMAIL"
    MATRIX = "MATRIX"
