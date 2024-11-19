from celery import shared_task
from core.logging import logger
from django.core.mail import send_mail

@shared_task
def notify_students_about_new_course(course_name, student_emails):
    try:
        logger.info(f"Notifying students about new course: {course_name}")
        for email in student_emails:
            send_mail(
                'New Course Available',
                f'A new course "{course_name}" has been added.',
                'admin@example.com',
                [email],
                fail_silently=False,
            )
        logger.info(f"Notification sent to all students about course: {course_name}")
    except Exception as e:
        logger.error(f"Error notifying students about new course {course_name}: {e}")
