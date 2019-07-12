import logging
from typing import List

import constants
from exceptions import ServiceAuthenticationError, UserTerminationError

_logger = logging.getLogger(__name__)


class InterfaceController(object):
    """Interface for all controllers used."""

    def run(self) -> bool:
        """ Runs a series of user inputs through the controller.

        Returns:
            True if the controller handled all user interactions,
                False otherwise.
        """
        raise NotImplementedError(
            f"`run` function was not defined for an"
            f" object inheriting from "
            f"InterfaceController."
        )

    @staticmethod
    def handle_input(prefix: str = ">> $: ") -> List[str]:
        """ Handles an input from the user, parses and verifies it and returns
            a split bash-like arg list.

        If an empty string is inputted (i.e. the user just pressed Enter),
        the user is re-prompted for an input.

        Args:
            prefix: The line prefix to use when prompting the user.

        Returns: A tuple of string arguments where each string is a space
                separated value from the user. The first element being the
                command itself, and subsequent being an arbirary,
                unchecked combination of flags and values.

        Raises:
            UserTerminationError: If the user inputted a command for the
                    controller to terminate.
        """
        command: str = ""
        while not command:
            command = input(prefix)

        if command.strip().lower() in constants.TERMINATION_COMMANDS:
            raise UserTerminationError()

        return command.split()

    def help(self, args: List[str]) -> bool:
        """ Prints a help message outlining the capabilities of this
            service controller.

        Args:
            args: User specified inputs such that args[0] is the command
                name itself.

        Return:
            True, if the use input was able to be processed, False otherwise.
        """
        raise NotImplementedError(
            f"{type(self)} has not defined a help function and inherits from "
            f"InterfaceController."
        )


class ServiceController(InterfaceController):
    """Base class for all controllers that operate a single service
        (e.g. Gmail, facebook). In future, will contain service specific
        functionality such as auth and config.
    """

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
        raise NotImplementedError(
            f"{type(self)} has not defined a `get_name` method but it inherits"
            f"from ServiceController."
        )

    def get_description(self) -> str:
        """ Returns the description of the service, shown to the user.
        """
        raise NotImplementedError(
            f"{type(self)} has not defined a `get_description` method but it"
            f" inherits from ServiceController."
        )

    def authenticate(self) -> bool:
        """ Allows the user to authenticate with the service.

        Returns:
            True upon successful authentication.
        Raises:
            ServiceAuthenticationError: If the user fails to authenticate.
        """
        raise NotImplementedError(
            f"{type(self)} has not defined a `authenticate` method but it"
            f" inherits from ServiceController."
        )

    def run(self) -> bool:
        """ Runs the looped interaction with the user.

        Upon termination, is responsible for closing down the Gmail client.

        Returns:
            True if the controller handled all user interactions and the gmail
                handler was successfully shut down, False otherwise.
        """
        try:
            self.authenticate()
            # Run until UserTerminationError
            while True:
                args: List[str] = ServiceController.handle_input(
                    prefix=f"{self.get_name()}>> $:"
                )
                if len(args) == 0:
                    self.help(args)
                else:
                    return self.process_args(args)

        except ServiceAuthenticationError:
            _logger.info(f"Could not authenticate {self.get_name()} service.")
        except UserTerminationError:
            _logger.debug(
                f"User has terminated interaction with {self.get_name()}"
                f" Controller."
            )
            return True

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
