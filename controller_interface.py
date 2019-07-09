from typing import List, Tuple

import constants
from exceptions import UserTerminationError


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
    def handle_input(prefix: str = ">> $: ") -> Tuple[str, ...]:
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
            command = input(prompt=prefix)

        if command.strip().lower() in constants.TERMINATION_COMMANDS:
            raise UserTerminationError()

        return tuple(command.split())

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
