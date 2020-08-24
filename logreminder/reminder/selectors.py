from calendar import monthrange
from datetime import datetime

from reminder.models import TeamMember, Worklog

def should_create_new_worklog(*, worklog: Worklog) -> bool:
    # This should be more intelligent but for now it suffice
    return worklog.created_at.month != datetime.now().month

def get_or_create_latest_worklog(*, member: TeamMember) -> Worklog:
    """
    Return latest existing Worklog of arg:member if it is not created more than a month ago
    otherwise create a new Worklog for arg:member and return that,
    """
    try:
        latest_worklog = member.worklogs.latest("created_at")
    except Worklog.DoesNotExist:
        latest_worklog = Worklog.objects.create(team_member=member)
    else:
        if should_create_new_worklog(worklog=latest_worklog):
            latest_worklog = Worklog.objects.create(team_member=member)

    return latest_worklog


def should_remind(worklog: Worklog) -> bool:
    # No need to remind if already pushed
    if worklog.pushed:
        return False

    never_notified = worklog.last_notified is None
    since_last_notification = lambda: datetime.now() - getattr(worklog, "last_notified",)

    return never_notified or since_last_notification().days >= 1
