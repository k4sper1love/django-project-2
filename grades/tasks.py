from celery import shared_task
from core.logging import logger
from django.core.mail import send_mail

@shared_task
def notify_student_about_new_grade(student_email, course_name, grade):
    try:
        logger.info(f"Sending grade notification to {student_email}")
        send_mail(
            'New Grade Assigned',
            f'You have received a new grade in {course_name}: {grade}.',
            'admin@example.com',
            [student_email],
            fail_silently=False,
        )
        logger.info(f"Grade notification sent to {student_email}")
    except Exception as e:
        logger.error(f"Error sending grade notification to {student_email}: {e}")
