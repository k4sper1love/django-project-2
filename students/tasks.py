from celery import shared_task
from core.logging import logger
from django.core.mail import send_mail

@shared_task
def notify_student_profile_update(student_email):
    try:
        logger.info(f"Sending profile update notification to {student_email}")
        send_mail(
            'Profile Updated',
            'Your student profile has been updated.',
            'admin@example.com',
            [student_email],
            fail_silently=False,
        )
        logger.info(f"Profile update notification sent to {student_email}")
    except Exception as e:
        logger.error(f"Error sending profile update notification to {student_email}: {e}")
