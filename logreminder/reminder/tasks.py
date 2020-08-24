from celery import shared_task
from celery.schedules import crontab
from django.db import transaction

from logreminder.celery import app
from reminder.models import TeamMember, Company
from reminder.selectors import get_or_create_latest_worklog
from reminder.services import remind_member


@shared_task
def remind_members_to_push_log():
    with transaction.atomic():
        for member in TeamMember.objects.filter(is_active=True):
            latest_worklog = get_or_create_latest_worklog(member=member)
            remind_member(member=member, latest_worklog=latest_worklog)


# Setup periodic tasks
app.add_periodic_task(
    crontab(minute=0, hour=9), remind_members_to_push_log.s(), name="remind team members to push log",
)
