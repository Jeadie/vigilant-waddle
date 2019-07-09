import argparse
import logging
import os
from typing import List, Tuple, Union

from exceptions import (
    ControllerCloseError,
    UserTerminationError
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

    def __init__(self, gmail: GmailHandler):
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
            ControllerCloseError: if the Gmail connection fails to close correctly.
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

    def run(self) -> bool:
        """ Runs the looped interaction with the user.

        Upon termination, is responsible for closing down the Gmail client.

        Returns:
            True if the controller handled all user interactions and the gmail
                handler was successfully shut down, False otherwise.
        """
        try:
            # Run until UserTerminationError
            while True:
                args: List[str] = GmailController.handle_input(prefix=f"{self.get_name()}>> $:")
                if len(args) == 0:
                    self.help(args)
                else:
                    {
                        "recent": self.recent,
                        "list": self.list,
                        "read": self.read,
                        "back": self.back,
                    }.get(args[0], self.help)(args)

        except UserTerminationError:
            _logger.debug(
                f"User has terminated interaction with Gmail Controller."
            )
            return True

    def recent(self, args: List[str]) -> bool:
        """ The function pattern for user commands to follow.

        Args:
            args: User specified inputs such that args[0] is the command
                name itself.

        Return:
            True, if the use input was able to be processed, False otherwise.
        """
        number = 10 if len(args) < 2 else args[1]
        number = int(number)
        messages = self.gmail.get_messages_from_query(
            "category:primary", max_messages=number,
        )
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
                query, max_messages=None if len(args) < 3 else args[2]
            )
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
                self.gmail.read_message(self.messages[index])

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
`list [query] [int]`: Lists the first [int] emails that match the query [query].
            If no int is provided, all emails matching the query are returned.
`read [int]`: Reads the indexed [int] from the previous list. [int] must be
        less than the number of emails in list. 
`back`: Prints the previous email list.
            """
        )
        return True