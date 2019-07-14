import logging
from typing import List

import google

import constants
from constants import GmailMessageFormat
from exceptions import (
    ControllerCloseError,
    NotAuthenticatedError,
    ServiceAuthenticationError,
    UserTerminationError,
)
from handler_gmail import GmailHandler
from controller_interface import ServiceController


_logger = logging.getLogger(__name__)


class GmailController(ServiceController):
    """ A controller for a user interacting with Gmail. Current
        commands include:
            - Get a list of emails, given a query.
            - Read an email's content.
            - Basic navigation between viewing an email and backtracking to
                the previous query.

    """

    def __init__(self, gmail: GmailHandler = None):
        """ Constructor.

        Args:
            gmail: A gmail handler to directly interact with Gmail.
        """
        self.gmail = gmail
        self.messages = []

    def close(self) -> bool:
        """ Closes down the connection to Gmail.

        Returns:
             True if the controller was successfully closed, False otherwise.
        Raises:
            ControllerCloseError: if the Gmail connection fails to close
                correctly.
        """
        if not self.gmail.close():
            raise ControllerCloseError()
        else:
            return True

    def get_description(self) -> str:
        """ Returns a description of Gmail to be seen by users.
        """
        return (
            f"This service allows you to view emails from your Gmail account."
        )

    def get_name(self) -> str:
        """ Returns the name of Gmail to be seen by users.
        """
        return "Gmail"

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

    def recent(self, args: List[str]) -> bool:
        """ The function pattern for user commands to follow.

        Args:
            args: User specified inputs such that args[0] is the command
                name itself.

        Return:
            True, if the use input was able to be processed, False otherwise.
        """
        number = (
            constants.GMAIL_DEFAULT_EMAIL_COUNT if len(args) < 2 else args[1]
        )
        number = int(number)
        messages = self.gmail.get_messages_from_query(
            constants.GMAIL_RECENT_QUERY,
            max_messages=number,
            form=GmailMessageFormat.METADATA,
        )
        self.messages = messages
        return self.gmail.print_email_list(emails=messages)

    def list(self, args: List[str]) -> bool:
        """ The function pattern for user commands to follow.

        Args:
            args: User specified inputs such that args[0] is the command
                name itself.

        Return:
            True, if the use input was able to be processed, False otherwise.
        """
        if len(args) < 2:
            print(
                f"Please provide a query with this command. "
                f"I.e. `list 'category:primary'`"
            )
        else:
            query = args[1]
            messages = self.gmail.get_messages_from_query(
                query,
                max_messages=None if len(args) < 3 else args[2],
                form=GmailMessageFormat.METADATA,
            )
            self.messages = messages
            return self.gmail.print_email_list(messages)

    def read(self, args: List[str]) -> bool:
        """ Displays a single email to the user.

        Args:
            args: User specified inputs such that args[0] is the command
                name itself.

        Return:
            True, if the use input was able to be processed, False otherwise.
        """
        if len(args) < 2:
            print("Please provide the index of email to read.")
            return False
        else:
            try:
                index = int(args[1])
                message_full = self.gmail.get_message_from_id(
                    self.messages[index]["id"], form=GmailMessageFormat.RAW
                )
                self.gmail.read_message(message_full)

            except ValueError:
                print(f"The value {args[1]} is not an integer.")
                return False

            except IndexError:
                print(
                    f"Index greater than number of messages. "
                    f"{int(args[1])}>={len(self.messages)}"
                )
                return False
            else:
                return True

    def back(self, args: List[str]) -> bool:
        """ Prints the previous message list requested by the used.

        Default use case is after a user has read a specific email.

        Args:
            args: User specified inputs such that args[0] is the command
                name itself.

        Return:
            True, if the use input was able to be processed, False otherwise.
        """
        if len(args) > 1:
            return False
        else:
            return self.gmail.print_email_list(self.messages)

    def help(self, args: List[str]) -> bool:
        """ Prints a help message outlining the capaiblities of the tool.

        Args:
            args: User specified inputs such that args[0] is the command
                name itself.

        Return:
            True, if the use input was able to be processed, False otherwise.
        """
        print(
            """
Not a valid command. Commands:
`recent [int]`: Lists last [int] emails from main inbox. Default 10.
`list [query] [int]`: Lists the first [int] emails matching the query [query].
            If no int is provided, all emails matching the query are returned.
`read [int]`: Reads the indexed [int] from the previous list. [int] must be
        less than the number of emails in list.
`back`: Prints the previous email list.
            """
        )
        return True

    def authenticate(self) -> bool:
        """ Allows the user to authenticate with the service.

        For gmail, it will first check if it has an active account. If so, it
        will confirm with the user if it wants to continue to use that
        authentication. If the user wants or has to authenticate then they
        are queried for a credentials file.
        Returns:
            True upon successful authentication.
        Raises:
            ServiceAuthenticationError: If the user fails to authenticate.
        """
        try:
            try:
                email = self.gmail.get_current_email()
                response = GmailController.handle_input(
                    prefix=f"You are currently authenticated as {email}."
                    f"Would you like to switch accounts? [y/n]"
                )
                if response[0].strip().lower() == "n":
                    return True
            except (NotAuthenticatedError, AttributeError):
                _logger.info(
                    f"No authentication is currently activated for service:"
                    f"{self.get_name()}."
                )

            credential_path = GmailController.handle_input(
                prefix="What is the path to the credentials file you would"
                "like to use?"
            )
            self.gmail = GmailHandler(credential_path)
            return True

        except google.auth.exceptions.DefaultCredentialsError as e:
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
