from django.db import models
from django.conf import settings

class APIRequestLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    status_code = models.IntegerField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.endpoint} - {self.method}"
