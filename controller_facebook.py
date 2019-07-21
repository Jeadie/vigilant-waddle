from datetime import datetime
import logging
from typing import List, Union, Dict
import getpass

from oauthlib.oauth2.rfc6749.errors import OAuth2Error

from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

from exceptions import UserTerminationError, ServiceAuthenticationError
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

    def __init__(self, facebook: Union[None, FacebookHandler] = None):
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
        return (
            "This service allows users to interact with their Facebook "
            "account."
        )

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
                    prefix=f"You are currently authenticated as "
                    f"{user['name']}. Would you like to switch "
                    f"accounts? [y/n]"
                )
                if response[0].strip().lower() == "n":
                    return True

            except (NotAuthenticatedError, AttributeError):
                _logger.info(
                    f"No authentication is currently activated for service:"
                    f"{self.get_name()}."
                )

            facebook_auth = OAuth2Session(
                constants.FACEBOOK_CLIENT_ID,
                redirect_uri=constants.FACEBOOK_REDIRECT_URI,
                scope=constants.FACEBOOK_OAUTH_SCOPES,
            )
            facebook_auth = facebook_compliance_fix(facebook_auth)
            authorization_url, state = facebook_auth.authorization_url(
                constants.FACEBOOK_AUTHORIZATION_BASE_URL
            )
            print("First, please go here and authorize,", authorization_url)

            # Get the authorization verifier code from the callback url
            redirect_response = input(
                "Second, paste the full redirect URL here:"
            )
            client_secret = getpass.getpass(
                prompt="Third, what is your Facebook client secret file: "
            )

            # Fetch the access token
            token = facebook_auth.fetch_token(
                constants.FACEBOOK_TOKEN_URI,
                client_secret=client_secret,
                authorization_response=redirect_response,
            )

            self.facebook = FacebookHandler(token)
            self.facebook.get_current_user(force_query=True)
            return True

        except FileNotFoundError:
            _logger.warning(
                "The facebook client secret specified does not exist."
            )
            raise ServiceAuthenticationError()

        except OAuth2Error as e:
            _logger.warning(
                f"An error occured when attempting to OAuth with Facebook."
                f" Error: {e}."
            )
            raise ServiceAuthenticationError()

        except NotAuthenticatedError:
            _logger.warning(
                f"An error occured when authenticated using with"
                f" Facebook Service."
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

        return {
            "recent": self.recent,
            "list": self.list,
            "read": self.read,
            "back": self.back,
        }.get(args[0], self.help)(args)

    def events(self, args: List[str]) -> bool:
        """ Displays a list of events for the user.

        Args:
            args:
              - [1]: The type of events to include.

        Returns:
            True, if events could be retrieved and listed.
        """
        if len(args) < 2 or args[1] not in constants.FACEBOOK_EVENT_TYPES:
            endpoint = f"/me/events?type={args[1]}"
        else:
            endpoint = f"/me/events"

        events = self.facebook.get_paginated_data(endpoint, limit=constants.FACEBOOK_EVENT_LIST_COUNT)
        print(
            f" i |         Event         | "
        )
        for e, i in zip(events, range(len(e))):
            if not self._event_print_line(e, i):
                return False

        self.datastore["events"] = e

    def _event_print_line(self, event_json: Dict[str, str], index: int) -> bool:
        """ Prints a single line detailing an event.

        Args:
            event_json: The JSON response of a single facebook event.
            index: The index associated with the event.

        Returns:
            True if the event JSON could be successfully parsed, False otherwise.
        """
        try:
            name = event_json['name']
            name = name[:20] + "..." if len(name) > 23 else name

            start_time = datetime.strptime(event_json["start_time"], constants.FACEBOOK_EVENT_DATETIME_FORMAT)
            start_time = start_time.strftime(constants.FACEBOOK_EVENT_DISPLAY_FORMAT)
            print(
                f"{index} {name}  {start_time}  {event_json['rsvp_status']}"
            )
        except KeyError as e:
            return False
        return True

    def _event_print_details(self, event_json: Dict[str, str]) -> bool:
        """ Prints the details of a single event to the user.

        Args:
            event_json: The JSON response of a single facebook event.

        Returns:
            True if the event JSON could be successfully parsed, False otherwise.
        """
        start_time = datetime.strptime(event_json["start_time"],
                                       constants.FACEBOOK_EVENT_DATETIME_FORMAT).strftime(constants.FACEBOOK_EVENT_DISPLAY_FORMAT)
        end_time =  datetime.strptime(event_json["end_time"],
                                       constants.FACEBOOK_EVENT_DATETIME_FORMAT).strftime(constants.FACEBOOK_EVENT_DISPLAY_FORMAT)

        print(f"Event:       {event_json['name']}")
        print(f"Start Time:  {start_time}")
        print(f"End Time:    {end_time}")
        print(f"Location:    {event_json['place']['name']}. {event_json['place']['street']} {event_json['place']['city']}, {event_json['place']['country']}")
        print(f"RSVP:        {event_json['rsvp_status']}")
        print(f"Description: {event_json['description']}")


    def event(self, args: List[str]) -> bool:
        """ Displays details of a specific event.

        Args:
            args:
              - [1] The index of the event to show details of.

        Returns:
            True if the event could be retrieved and displayed.
        """
        if len(args) != 2:
            print("  Please specify an event index.")
            return False

        i = int(args[1])
        if self.datastore.get("events") and i < len(self.datastore["events"]):
            print(
                f"Index {i} must be between 0 & {len(self.datastore['events'])}."
            )
            return False

        return self._event_print_details(self.datastore["events"][i])
