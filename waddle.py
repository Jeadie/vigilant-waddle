import argparse
import logging

from controller_gmail import GmailController
from controller_facebook import FacebookController
from controller_main import MainController

_logger = logging.getLogger(__name__)


if __name__ == "__main__":
    _logger.setLevel(logging.DEBUG)
    DEFAULT_CREDENTIAL_PATH = "credentials-je.dat"
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose", "-v", default=0, action="count", help="verbosity"
    )
    arguments = parser.parse_args()

    service_controller = [GmailController(), FacebookController()]
    main_controller = MainController(service_controller)
    main_controller.run()
