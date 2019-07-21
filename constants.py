from typing import Tuple
from enum import Enum


TERMINATION_COMMANDS: Tuple[str, ...] = ("quit", "exit")

# Facebook constants
FACEBOOK_CLIENT_ID = "1565657260242806"
FACEBOOK_REDIRECT_URI = "https://www.facebook.com/connect/login_success.html"
FACEBOOK_AUTHORIZATION_BASE_URL = "https://www.facebook.com/dialog/oauth"
FACEBOOK_TOKEN_URI = "https://graph.facebook.com/oauth/access_token"
FACEBOOK_API_VERSION = "3.3"
FACEBOOK_OAUTH_SCOPES = [
    # "default",
    "email",
    "groups_access_member_info",
    "publish_to_groups",
    "user_age_range",
    "user_birthday",
    "user_events",
    "user_friends",
    "user_gender",
    "user_hometown",
    "user_likes",
    "user_link",
    "user_location",
    "pages_messaging",
    "user_photos",
    "user_posts",
    "user_tagged_places",
    "user_videos",
]

FACEBOOK_EVENT_TYPES = [
    "attending",
    "created",
    "declined",
    "maybe",
    "not_replied"
]
FACEBOOK_EVENT_LIST_COUNT = 10
FACEBOOK_EVENT_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
FACEBOOK_EVENT_DISPLAY_FORMAT = "%c"

# Gmail Constants
GMAIL_DEFAULT_EMAIL_COUNT = 10
GMAIL_RECENT_QUERY = "category:primary"


class GmailMessageFormat(Enum):
    FULL = "full"
    METADATA = "metadata"
    MINIMAL = "minimal"
    RAW = "raw"
