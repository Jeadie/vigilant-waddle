import logging
from typing import List, Union
import getpass

from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

from exceptions import (
    UserTerminationError,
    ServiceAuthenticationError
)
import constants
from exceptions import NotAuthenticatedError
from controller_interface import ServiceController
from handler_facebook import FacebookHandler

_logger = logging.getLogger(__name__)


class FacebookController(ServiceController):
    """Base class for all controllers that operate a single service
        (e.g. Gmail, facebook). In future, will contain service specific
        functionality such as auth and config.
    """

    def __init__(self, facebook : Union[None, FacebookHandler] = None):
        """

        Returns:
            Constructor.

        Raises:
            None.
        """
        self.facebook = facebook

    def close(self) -> bool:
        """ Performs all necessary operations to properly close the
            service controller.

            Returns:
                True, if the controller was able to close itself down
                properly, False otherwise.
            Raises:
                ControllerCloseError: if the controller cannot properly close.
        """
        raise NotImplementedError(
            f"{type(self)} has not defined a close method but it inherits"
            f"from ServiceController."
        )

    def get_name(self) -> str:
        """ Returns the name of the service, shown to the user.
        """
        return "Facebook"

    def get_description(self) -> str:
        """ Returns the description of the service, shown to the user.
        """
        return "This service allows users to interact with their Facebook" \
               "account."

    def authenticate(self) -> bool:
        """ Allows the user to authenticate with the service.

        Returns:
            True upon successful authentication.
        Raises:
            ServiceAuthenticationError: If the user fails to authenticate.
        """
        try:
            try:
                user = self.facebook.get_current_user()
                response = FacebookController.handle_input(
                    prefix=f"You are currently authenticated as {user['name']}."
                           f"Would you like to switch accounts? [y/n]"
                )
                if response[0].strip().lower() == "n":
                    return True

            except (NotAuthenticatedError, AttributeError):
                _logger.info(
                    f"No authentication is currently activated for service:"
                    f"{self.get_name()}."
                )
            facebook_auth = OAuth2Session(constants.FACEBOOK_CLIENT_ID, redirect_uri=constants.FACEBOOK_REDIRECT_URI)
            facebook_auth = facebook_compliance_fix(facebook_auth)
            authorization_url, state = facebook_auth.authorization_url(
                constants.FACEBOOK_AUTHORIZATION_BASE_URL)
            print('Please go here and authorize,', authorization_url)

            # Get the authorization verifier code from the callback url
            redirect_response = input('Paste the full redirect URL here:')
            file_secret = getpass.getpass(prompt="Path to the Facebook client secret file: ")
            with open(file_secret, "r") as f:
                client_secret = f.read()

            # Fetch the access token
            token = facebook_auth.fetch_token(constants.FACEBOOK_TOKEN_URI,
                                              client_secret=client_secret,
                                              authorization_response=redirect_response)

            self.facebook = FacebookHandler(token)
            return True

        except ZeroDivisionError as e: # TODO: facebook errors
            _logger.warning(
                f"An error occured when using the credentials file to"
                f"authenticate a Gmail connection. Error: {e}."
            )
            raise ServiceAuthenticationError()

        except UserTerminationError:
            raise ServiceAuthenticationError(
                f"Failed to authenticate into {self.get_name()} service. User"
                f"terminated interaction."
            )


    def process_args(self, args: List[str]) -> bool:
        """Processes a set of arguments from the user.

        Args:
            args: A list of strings typed by the user.

        Returns:
            True, if the service controller successfully processed the args,
                False otherwise.
        """
        raise NotImplementedError(
            f"{type(self)} has not defined a `process_args` method but it"
            f" inherits from ServiceController"
        )
