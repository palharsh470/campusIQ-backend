import logging
from celery import shared_task
from django.core.mail import EmailMessage
from .models import Announcement
from notifications.models import Notification
from notifications.services import notify

logger = logging.getLogger(__name__)


@shared_task
def send_announcement_email(announcement_id):

    announcement = Announcement.objects.select_related("class_group").get(pk=announcement_id)

    if announcement.status != Announcement.Status.PENDING :
        return

    student_emails = announcement.class_group.enrollments.values_list('student__email', flat = True)

    try :
        if not student_emails :
            raise ValueError("No students enrolled in this class.")

        EmailMessage(
            subject=announcement.subject,
            body=announcement.message,
            to=[],
            bcc=student_emails,
        ).send(fail_silently=False)

    except Exception as e:
        logger.exception("Announcement %s failed", announcement_id)
        announcement.status = Announcement.Status.FAILED
        announcement.error = str(e)
        announcement.save(update_fields=['status', 'error'])
        notify(
        announcement.teacher,
        Notification.Kind.ERROR,
        f'Announcement "{announcement.subject}" could not be sent.',
        )
        return

    announcement.status = Announcement.Status.SENT
    announcement.recipient_count = len(student_emails)
    announcement.save(update_fields=['status', 'recipient_count'])
    notify(
        announcement.teacher,
        Notification.Kind.SUCCESS,
        f'Announcement "{announcement.subject}" was sent to {len(student_emails)} students.',
    )