class UserTerminationError(Exception):
    """ This exception is raised when a user has decided to terminate use of
        the current controller.
    """

    pass


class ControllerCloseError(Exception):
    """ This exception is raised when a controller fails to close correctly.

    """

    pass


class ServiceAuthenticationError(Exception):
    """ This exception is raised when a user cannot authenticate with a service.

    """

    pass


class NotAuthenticatedError(Exception):
    """ This exception is raised when a service handler is not authenticated
        when it expects to be.

    """

    pass
