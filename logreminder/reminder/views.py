from django.shortcuts import HttpResponse, get_object_or_404
from django.utils import timezone

from reminder.models import Worklog


def confirm(request, worklog_uuid):
    worklog: Worklog = get_object_or_404(Worklog, pk=worklog_uuid)
    worklog.pushed, worklog.pushed_at = True, timezone.now()
    worklog.save()
    return HttpResponse("Thank you for confirmation.")
