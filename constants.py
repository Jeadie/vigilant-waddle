from typing import Tuple
from enum import Enum


TERMINATION_COMMANDS: Tuple[str, ...] = ("quit", "exit")

# Facebook constants
FACEBOOK_CLIENT_ID = "1565657260242806"
FACEBOOK_REDIRECT_URI = "https://www.facebook.com/connect/login_success.html"
FACEBOOK_AUTHORIZATION_BASE_URL = "https://www.facebook.com/dialog/oauth"
FACEBOOK_TOKEN_URI = "https://graph.facebook.com/oauth/access_token"

# Gmail Constants
GMAIL_DEFAULT_EMAIL_COUNT = 10
GMAIL_RECENT_QUERY = "category:primary"


class GmailMessageFormat(Enum):
    FULL = "full"
    METADATA = "metadata"
    MINIMAL = "minimal"
    RAW = "raw"
