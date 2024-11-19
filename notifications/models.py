from django.db import models
from users.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('course', 'Course Notification'),
        ('general', 'General Notification'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='general')

    def __str__(self):
        status = "Read" if self.read else "Unread"
        return f"Notification for {self.user.username}: {status}"
