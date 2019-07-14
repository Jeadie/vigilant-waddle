import json
import logging
from typing import List, Dict

import facebook

import constants
from exceptions import NotAuthenticatedError

_logger = logging.getLogger(__name__)


class FacebookHandler(object):
    """

    """

    def __init__(self, token: Dict[str, str]):
        """
        Args:
            token:

        Returns:
             Constructor.
        """
        self.api = facebook.GraphAPI(access_token=token["access_token"], version=constants.FACEBOOK_API_VERSION)
        self.token = token

    def get_current_user(self) -> Dict[str, str]:
        """ Returns the current user from the Facebook API.

        Returns:
             A user dictionary from the Facebook Graph API. Keys: name, id.
        Raises:
            NotAuthenticatedError: If the service handler is not authenticated.
        """


    def close(self) -> bool:
        """ Closes down the connection with the API.

        After an instance calls this method, it is essentially unusable.

        Returns:
            True if Facebook connection was properly ended, False otherwise.
        """
        raise NotImplementedError()
