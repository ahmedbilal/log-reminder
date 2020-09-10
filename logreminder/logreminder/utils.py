from urllib.parse import urlunparse, urlparse, urljoin
from django.conf import settings


def get_base_domain() -> str:
    protocol, domain, port = settings.PROTOCOL, settings.DOMAIN, settings.PORT
    parsed_url = urlparse(f"{protocol}://{domain}")
    parsed_url = parsed_url if port == 80 else parsed_url._replace(netloc=parsed_url.netloc + f":{port}")
    return urlunparse(parsed_url)


def build_absolute_url(postfix) -> str:
    return urljoin(get_base_domain(), str(postfix))
