import argparse
import os
import logging

from handler_gmail import GmailHandler
from controller_gmail import GmailController
from controller_main import MainController

if __name__ == "__main__":
    DEFAULT_CREDENTIAL_PATH = "credentials-je.dat"
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose", "-v", default=0, action="count", help="verbosity"
    )
    parser.add_argument(
        "--credentials",
        "-c",
        default=False,
        help="Gmail credentials to use when authenticating with Gmail API.",
    )
    arguments = parser.parse_args()
    logging.set_severity_from_verbosity(arguments.verbose)

    if arguments.credentials:
        gmail = GmailHandler(DEFAULT_CREDENTIAL_PATH)

    elif os.path.exists(DEFAULT_CREDENTIAL_PATH):
        gmail = GmailHandler(DEFAULT_CREDENTIAL_PATH)
    else:
        print(
            "No credentials were passed in and there were no default "
            f"credentials set. Cannot run."
        )
        exit(1)

    g_controller = GmailController(gmail)

    main_controller = MainController([g_controller])
    main_controller.run()
