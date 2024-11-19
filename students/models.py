from django.db import models
from users.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    dob = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    registration_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.user.email}"

    class Meta:
        permissions = [
            ("view_all_students", "Can view all students"),
            ("view_own_students", "Can view own students"),
        ]
