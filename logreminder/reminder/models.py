import uuid

from django.db import models
from django.utils import timezone

from reminder.data import CommunicationMedium


class Company(models.Model):
    name = models.CharField(max_length=128)
    email = models.CharField(max_length=128, help_text="")
    communication_configuration = models.JSONField(
        blank=True,
        null=True,
        help_text="""\
        {
            "matrix_domain": "https://matrix.example.com/",
            "matrix_user_facing_domain": "https://example.com/",
            "matrix_user": "user",
            "matrix_password": "password",
            "matrix_room_id": "room_id:example.com"
        }

        Note matrix_room_id must begin with !.
        """,
    )

    def __str__(self):
        return str(self.name)


class TeamMember(models.Model):
    name = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    company = models.ForeignKey(Company, related_name="members", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)


class Communication(models.Model):
    value = models.CharField(max_length=128)
    type = models.CharField(max_length=32, choices=CommunicationMedium.choices)
    team_member = models.ForeignKey(TeamMember, related_name="communications", on_delete=models.CASCADE)


class Worklog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team_member = models.ForeignKey(TeamMember, related_name="worklogs", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    pushed = models.BooleanField(default=False)
    pushed_at = models.DateTimeField(blank=True, null=True)
    last_notified = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"(name={self.team_member.name}, created_at={self.created_at.date()}, pushed={self.pushed}"
