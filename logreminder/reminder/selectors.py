from typing import Optional

from django.utils import timezone

from reminder.models import TeamMember, Worklog


def should_create_new_worklog(worklog: Optional[Worklog]) -> bool:
    # If a worklog exists and it is created in this month, we shouldn't create a new worklog
    if worklog and worklog.created_at.month == timezone.now().month:
        return False

    return timezone.now().day == 1


def get_or_create_latest_worklog_if_reasonable(*, member: TeamMember) -> Optional[Worklog]:
    """
    Return latest existing Worklog of arg:member if it is not created more than a month ago
    otherwise create a new Worklog for arg:member and return that,
    """
    try:
        latest_worklog = member.worklogs.latest("created_at")
    except Worklog.DoesNotExist:
        latest_worklog = None

    return (
        Worklog.objects.create(team_member=member)
        if should_create_new_worklog(worklog=latest_worklog)
        else latest_worklog
    )


def should_remind(worklog: Worklog) -> bool:
    # No need to remind if already pushed
    if worklog.pushed:
        return False

    never_notified = worklog.last_notified is None
    since_last_notification = lambda: timezone.now() - getattr(worklog, "last_notified",)

    return never_notified or since_last_notification().total_seconds() >= 3600 * 16
