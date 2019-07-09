from typing import List, Tuple, Union
import logging

from exceptions import ControllerCloseError, UserTerminationError
from controller_interface import InterfaceController, ServiceController


_logger = logging.getLogger(__name__)


class MainController(InterfaceController):
    """ The controller to to operate all sub-controllers. Currently includes:
            - GmailController
    """

    def __init__(self, sub_controllers: List[InterfaceController]):
        self.controllers = sub_controllers

    def run(self) -> bool:
        """ Main loop controller responsible for

        Returns: True if the controller managed to handle all use inputs and
            closed down any necessary connections or services.
        """
        try:
            # Run until UserTerminationError
            while True:
                args: Tuple[str, ...] = MainController.handle_input()

                if len(args) > 1:
                    self.help()
                    continue
                sub_controller: Union[None, ServiceController] = next(
                    [c for c in self.controllers if c.get_name() == args[0]],
                    default=None,
                )
                if not sub_controller:
                    print(
                        f"{args[0]} is not a valid service."
                    )
                    self.help()
                else:
                    if not sub_controller.run():
                        _logger.warning(
                            f"Controller, {sub_controller.get_name()} had a"
                            f"problem running."
                        )

        except UserTerminationError:
            _logger.debug(
                f"User has terminated interaction with Main Controller."
            )
            for controller in self.controllers:
                try:
                    controller.close()
                except ControllerCloseError as e:
                    _logger.error(
                        f"Controller: {type(controller)} failed to"
                        f"close properly. Error: {e}."
                    )
                    return False
                else:
                    _logger.info(f"Main Controller successfully terminated.")
                    return True

    def help(self) -> bool:
        """Prints a help message to the user, outlining all the available
            services.

        Returns:
            True, if the message was able to be printed.
        """
        print("Please select a service to use:")
        for controller in self.controllers:
            print(
                f"Name: {controller.get_name()}. "
                f"Description: {controller.get_description()}"
            )
        return True

