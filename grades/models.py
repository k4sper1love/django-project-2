from django.db import models
from courses.models import Course
from students.models import Student
from users.models import User

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2)
    comment = models.TextField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})

    def __str__(self):
        return f"Grade {self.grade} for {self.student.user.username} in {self.course.name}"
