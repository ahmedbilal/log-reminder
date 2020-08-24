from datetime import datetime
from uuid import UUID

from django.core.mail import EmailMultiAlternatives
from django.urls import reverse_lazy

from reminder.data import CommunicationMedium
from reminder.models import TeamMember, Worklog
from reminder.selectors import should_remind
from reminder.matrix import MatrixClient

from urllib.parse import urljoin
from logreminder.utils import get_base_domain, build_absolute_url


def send_confirmation_email(*, sender_email:str, receiver_email: str, worklog_uuid: UUID) -> None:
    subject, from_email, to_email = (
        "Push your worklog!",
        sender_email,
        receiver_email,
    )

    confirmation_link = build_absolute_url(reverse_lazy("confirm", kwargs={"worklog_uuid": worklog_uuid}))
    text_content = f"""\
    Open the following link in your browser to confirm that you have pushed your worklogs.

    {confirmation_link}
    """

    html_content = f"""\
    Click <a href="{confirmation_link}">here</a> to confirm that you have pushed your worklogs.
    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def send_confirmation_matrix_message(*, company_configuration: dict, communication_value, worklog_uuid) -> None:
    matrix_domain = company_configuration["matrix_domain"]
    matrix_user_facing_domain = company_configuration["matrix_user_facing_domain"]
    matrix_user = company_configuration["matrix_user"]
    matrix_password = company_configuration["matrix_password"]

    matrix_client = MatrixClient(
        domain=matrix_domain,
        user_facing_domain=matrix_user_facing_domain,
        user=matrix_user,
        password=matrix_password,
    )
    confirmation_link = build_absolute_url(reverse_lazy("confirm", kwargs={"worklog_uuid": worklog_uuid}))

    matrix_message = f"""\
    {matrix_client.mention(communication_value)} Click <a href="{confirmation_link}">here</a> to confirm that you have pushed your worklogs.
    """
    matrix_client.send_message(matrix_message, company_configuration["matrix_room_id"])

def remind_member(*, member: TeamMember, latest_worklog: Worklog) -> None:
    if should_remind(worklog=latest_worklog):
        for communication in member.communications.all():
            if communication.type == CommunicationMedium.EMAIL:
                send_confirmation_email(
                    sender_email=member.company.email,
                    receiver_email=communication.value,
                    worklog_uuid=latest_worklog.id
                )
            elif communication.type == CommunicationMedium.MATRIX:
                company_configuration = member.company.communication_configuration
                send_confirmation_matrix_message(
                    company_configuration=company_configuration,
                    communication_value=communication.value,
                    worklog_uuid=latest_worklog.id
                )

            latest_worklog.last_notified = datetime.now()
            latest_worklog.save()
