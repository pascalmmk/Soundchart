from django.conf import settings
from django.db import models

class OAuthToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    provider = models.CharField(max_length=32, default="spotify")
    access_token = models.TextField()
    refresh_enc = models.BinaryField()
    expires_at = models.DateTimeField()
    scope = models.TextField(blank=True, default="")
    token_type = models.CharField(max_length=16, default="Bearer")

    class Meta:
        unique_together = ("user", "provider")
