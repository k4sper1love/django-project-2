from celery import shared_task
from .models import Notification
from core.logging import logger

@shared_task
def create_course_notification(course_name, user_ids):
    try:
        logger.info(f"Creating notifications for new course: {course_name}")
        for user_id in user_ids:
            Notification.objects.create(
                user_id=user_id,
                message=f"A new course '{course_name}' has been added. Check it out!"
            )
        logger.info(f"Notifications created for new course: {course_name}")
    except Exception as e:
        logger.error(f"Error creating notifications for new course {course_name}: {e}")
