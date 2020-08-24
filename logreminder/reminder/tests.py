from datetime import datetime, timedelta
from uuid import uuid4

from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy
from freezegun import freeze_time

from reminder.data import CommunicationMedium
from reminder.models import TeamMember, Company
from reminder.services import send_confirmation_email
from reminder.tasks import remind_members_to_push_log

from logreminder.utils import get_base_domain, build_absolute_url
from urllib.parse import urljoin

class TestUtils(TestCase):
    def test_absolute_url_formation(self):
        """
        Test that get_base_domain() returns same url whether DOMAIN contains / as postfix or not
        also get_base_domain() shouldn't append port if PORT is 80
        """
        example_uuid = "ff0a0071-7f08-4683-b814-d4dc834f2de8"

        with self.settings(DOMAIN="localhost", PORT=8000):
            self.assertEqual(
                build_absolute_url(reverse_lazy("confirm", kwargs={"worklog_uuid": example_uuid})),
                f"http://localhost:8000/confirm/ff0a0071-7f08-4683-b814-d4dc834f2de8"
            )

        with self.settings(DOMAIN="localhost/", PORT=8000):
            self.assertEqual(
                build_absolute_url(reverse_lazy("confirm", kwargs={"worklog_uuid": example_uuid})),
                "http://localhost:8000/confirm/ff0a0071-7f08-4683-b814-d4dc834f2de8"
            )

        with self.settings(DOMAIN="localhost", PORT=80):
            self.assertEqual(
                build_absolute_url(reverse_lazy("confirm", kwargs={"worklog_uuid": example_uuid})),
                "http://localhost/confirm/ff0a0071-7f08-4683-b814-d4dc834f2de8"
            )


class TestEmail(TestCase):
    def test_send_confirmation_email(self):
        send_confirmation_email(sender_email="sender@example.com", receiver_email="abc@example.com", worklog_uuid=uuid4())
        self.assertEqual(len(mail.outbox), 1, "Email isn't being sent")


class TestTasks(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

    def setUp(self):
        self.company = Company.objects.create(name="example", email="ctt@example.com")

        self.inactive_member = TeamMember.objects.create(name="inactive", is_active=False, company=self.company)
        self.inactive_member.communications.create(type=CommunicationMedium.EMAIL, value="inactive@example.com")

        self.first = TeamMember.objects.create(name="first", is_active=True, company=self.company)
        self.first.communications.create(type=CommunicationMedium.EMAIL, value="first@example.com")

        self.second = TeamMember.objects.create(name="second", is_active=True, company=self.company)
        self.second.communications.create(type=CommunicationMedium.EMAIL, value="second@example.com")

    def total_emails_sent(self):
        return len(mail.outbox)

    def confirm_latest_worklog(self, member):
        # I don't see a point to put confirm_latest_log into the Model manager of TeamMember yet

        def confirm_worklog(client, _id):
            return client.get(reverse("confirm", kwargs={"worklog_uuid": _id}))

        return confirm_worklog(self.client, getattr(member.worklogs.latest("created_at"), "id", None))

    def test_basic_send_email(self):
        remind_members_to_push_log()
        self.assertEqual(self.total_emails_sent(), 2)

    def test_calling_send_email_twice_does_not_result_in_duplication(self):
        # TODO: Compare Worklog.objects.all() before and after the second remind_members_to_push_log()

        remind_members_to_push_log()
        self.assertEqual(self.total_emails_sent(), 2)

        # The below send mail shouldn't have any effect at all
        remind_members_to_push_log()
        self.assertEqual(self.total_emails_sent(), 2, "Emails sent on repeated task execution when it shouldn't")

    def test_email_reminder_sent_if_member_dont_confirm(self):
        remind_members_to_push_log()
        self.assertEqual(self.total_emails_sent(), 2)

        with freeze_time(str(datetime.now() + timedelta(days=1))):
            remind_members_to_push_log()
            self.assertEqual(self.total_emails_sent(), 4)

    def test_no_reminder_send_if_everyone_confirmed_their_worklogs(self):
        remind_members_to_push_log()
        self.assertEqual(self.total_emails_sent(), 2)
        self.confirm_latest_worklog(self.first)
        self.confirm_latest_worklog(self.second)

        remind_members_to_push_log()
        self.assertEqual(self.total_emails_sent(), 2)

    def test_partial_email_reminder_sent_if_member_dont_confirm(self):
        remind_members_to_push_log()

        self.confirm_latest_worklog(self.first)

        # Now, we are left with only second user as the first has confirmed
        with freeze_time(str(datetime.now() + timedelta(days=1))) as fronzen_datetime:
            # After 1 day, send_email should be triggered and it should send a reminder email
            remind_members_to_push_log()
            self.assertEqual(self.total_emails_sent(), 3)

            # Winding clock forward to the next day, send_email should be triggered
            # and it should send a reminder email
            fronzen_datetime.tick(timedelta(days=1))
            remind_members_to_push_log()
            self.assertEqual(self.total_emails_sent(), 4)

            # Second user also confirms his/her worklog
            self.confirm_latest_worklog(self.second)

            # Winding clock forward to the next day, send_email should be triggered
            # but it should not send a reminder email as everyone has pushed their
            # worklogs
            fronzen_datetime.tick(timedelta(days=1))
            remind_members_to_push_log()
            self.assertEqual(self.total_emails_sent(), 4)

    def test_worklog_created_next_month(self):
        remind_members_to_push_log()
        self.assertEqual(self.total_emails_sent(), 2)

        self.confirm_latest_worklog(self.first)
        self.confirm_latest_worklog(self.second)

        with freeze_time(str(datetime.now() + timedelta(days=30))):
            remind_members_to_push_log()
            self.assertEqual(self.total_emails_sent(), 4)
