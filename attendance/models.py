from django.db import models
from courses.models import Course
from students.models import Student

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.BooleanField()

    def __str__(self):
        status = "Present" if self.status else "Absent"
        return f"{self.student.user.username} - {status} on {self.date}"
