class UserTerminationError(Exception):
    """ This exception is raised when a user has decided to terminate use of
        the current controller.
    """

    pass


class ControllerCloseError(Exception):
    """ This exception is raised when a controller fails to close correctly.

    """

    pass
