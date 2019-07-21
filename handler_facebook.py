import logging
from typing import List, Dict
import requests

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
        self.session = requests.Session()
        self.api = facebook.GraphAPI(
            access_token=token["access_token"],
            session=self.session,
            version=constants.FACEBOOK_API_VERSION,
        )
        self.token = token
        self._user = None

    def get_current_user(self, force_query: bool = False) -> Dict[str, str]:
        """ Returns the current user from the Facebook API.

        Args:
            force_query: if True, the service will not use any cached user
                details. If False, will use cached user details if they exist.

        Returns:
             A user dictionary from the Facebook Graph API. Keys: name, id.
        Raises:
            NotAuthenticatedError: If the service handler could not provide
                the user details either from the cache or if the service is
                not authenticated.
        """
        if not force_query and self._user:
            return self._user

        try:
            self._user = self.api.request("/me")
            return self._user
        except facebook.GraphAPIError as e:
            raise NotAuthenticatedError(
                f"No current user is logged in. Error occurred {e}."
            )

    def close(self) -> bool:
        """ Closes down the connection with the API.

        After an instance calls this method, it is essentially unusable.

        Returns:
            True if Facebook connection was properly ended, False otherwise.
        """
        self.session.close()
        return True

    def get_paginated_data(self, endpoint: str, limit: int = -1) -> List[Dict[str, str]]:
        """ Returns cursor-paginated data from an endpoint. It is assumed the endpoint
            supports pagination checks.

        Args:
            endpoint: The endpoint to query.
            limit: The number of paginated results to return. If None, will return all
                paginated results.

        Returns:
            A list of JSON response results. Subsequent paginations will be appended
                in order.
        """
        p = 0
        finished = False
        results = []
        while (p != limit) and not finished:
            page = self.api(endpoint)
            results.extend(page.get("data"), [])

            if page.get("paging") and page.get("paging").get("next"):
                endpoint = page.get("paging").get("next")
            else:
                finished = True

            p += 1
        return results

