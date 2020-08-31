import re

from functools import reduce
from urllib.parse import urljoin, urlparse

import bleach
import requests


class MatrixClient:
    def __init__(self, domain, user_facing_domain, user, password):
        self.user_facing_domain = urlparse(user_facing_domain).hostname
        self.domain = domain
        self.user = user
        self.password = password

        self.api_url = self._join_urls(self.domain, "_matrix", "client", "r0")

    def _join_urls(self, *url_fragments):
        urls_ending_with_forward_slash = map(lambda url: url + "/" if not url.endswith("/") else url, url_fragments)
        return reduce(urljoin, urls_ending_with_forward_slash)

    def _get_auth_token(self):
        login_url = urljoin(self.api_url, "login")
        auth_request_body = {"type": "m.login.password", "user": self.user, "password": self.password}
        auth = requests.post(login_url, json=auth_request_body, timeout=30)
        return auth.json()["access_token"]

    def mention(self, username):
        re_result = re.match(r"@(\w+):\w+\.\w+", username)
        # Handle case in which the user is coming from some other federated server
        if re_result:
            return f'<a href="https://matrix.to/#/{re_result.group(0)}">{re_result.group(1)}</a>'
        else:
            return f'<a href="https://matrix.to/#/@{username}:{self.user_facing_domain}">{username}</a>'

    def send_message(self, message, room_id):
        send_message_url = urljoin(
            self._join_urls(self.api_url, "rooms", room_id, "send"),
            f"m.room.message?access_token={self._get_auth_token()}",
        )
        plain_message = bleach.clean(message, strip=True, tags=[])
        send_message_request_body = {
            "msgtype": "m.text",
            "body": plain_message,
            "format": "org.matrix.custom.html",
            "formatted_body": message,
        }
        return requests.post(send_message_url, json=send_message_request_body, timeout=30)
