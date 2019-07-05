import argparse
import base64
import email
import logging
import os
from typing import List, Dict

from oauth2client.file import Storage
from apiclient.discovery import build
import html2text

DEFAULT_CREDENTIAL_PATH = "credentials-je.dat"
_logger = logging.getLogger(__name__)


class GmailHandler(object):
    """
        A custom client to handle authentication and common requests of the
        gmail API.
    """

    def __init__(self, cred_file):
        """

        Args:
            cred_file: An credential file for the oauth2 client.

        Returns:
             Constructor.
        """
        self.cred = Storage(cred_file).get()
        self.service = build('gmail', 'v1', credentials=self.cred)

    def close(self) -> bool:
        """ Closes down the connection with the API.

        After an instance calls this method, it is essentially unusable.

        Returns:
            True if Gmail connection was properly ended, False otherwise.
        """
        # TODO: investigate closing down gmail.
        return True

    def get_message_from_id(self, id: str, form: str = "raw",
                            metadata: List[str] = None) -> Dict[str, str]:
        """ Gets a Message object, given its ID.

        Args:
            id: Id of a email.
            form: The format of email to return, options are: 'full', 'metadata', 'minimal', 'raw'.
                            See https://developers.google.com/gmail/api/v1/reference/users/messages/get
            metadata: metadata headers to include when receiving messages.

        Returns:
            A message Object.

        Raises:
            TBD
        """
        if metadata:
            return self.service.users().messages().get(userId="me", id=id,
                                                       format=form,
                                                       metadataHeaders=metadata).execute()
        else:
            return self.service.users().messages().get(userId="me", id=id,
                                                       format=form).execute()

    def print_email_list(self, emails):
        """ Prints a list of email previews, including the name of the sender
            and a snippet of the message.

        Args:
            emails: A list of message objects from the Gmail API.

        Return:
            True if the list of emails was successfully sent to stdout, False otherwise.
        """
        try:
            for m, i in zip(emails, range(len(emails))):
                From = m["payload"]["headers"]
                From = next(x["value"] for x in From if x["name"] == "From")
                From = f"{(45 - len(From)) * ' '}{From}"
                index = f"{((len(emails) // 10) - (i // 10)) * ' '}{i}"
                print(f"|{index}|{From} | {m['snippet'][:140]} ")
        except KeyError as e:
            _logger.error(
                f"An Gmail message object did not have expected keys. Error: {e}."
            )
            return False
        else:
            return True

    def get_messages_from_query(self, query, form: str = "raw",
                                metadata: List[str] = None,
                                max_messages: int = None) -> List[
        Dict[str, str]]:
        """ Returns complete message objects for a single query.

        :param query: A query string to filter emails with. Same format as string
            filtering in the gmail GUI.
        :param form: The form of email to return, options are: 'full', 'metadata', 'minimal', 'raw'.
                        See https://developers.google.com/gmail/api/v1/reference/users/messages/get
        :param max_messages: The maximum number of messages to retrieve from
                             gmail servers. If not set, all messages matching
                             the filter will be returned.
        :return: A list of Message objects filtered by the given query.
        """
        messages = self.service.users().messages().list(userId="me",
                                                        q=query).execute()
        if max_messages:
            return [
                self.get_message_from_id(m["id"], form=form, metadata=metadata)
                for m in messages["messages"][0:max_messages]]
        else:
            return [
                self.get_message_from_id(m["id"], form=form, metadata=metadata)
                for m in messages["messages"]]

    def read_message(self, message: Dict[str, str]) -> bool:
        """ Given an index, prints the corresponding message from the previous list.

        Args:
            message: the message object to be printed, in detail with

        Returns:
            True, if it was successful in displaying the email. False otherwise.

        """
        # TODO: Think of a better way to represent individual emails.
        #  The current, dumps the html out to stdout.
        # Ideas:
        #   Render in browser, pop-up.
        #   Filter html tags.
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

        mime_msg = email.message_from_string(msg_str.decode())
        print(f"From: {mime_msg['From']}")
        print(f"Date: {mime_msg['Date']}")
        h = html2text.HTML2Text()
        h.ignore_links = True

        if mime_msg.is_multipart():
            for payload in mime_msg.get_payload():
                print(h.handle(payload.get_payload(decode=False)))
        else:
            print(h.handle(mime_msg.get_payload(decode=False)))


class GmailController(object):
    """ A controller for a user interacting with Gmail. Current commands include:
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

    def run(self) -> bool:
        """ Runs the looped interaction with the user.

        Upon termination, is responsible for closing down the Gmail client.

        Returns:
            True if the controller handled all user interactions and the gmail
                handler was successfully shut down, False otherwise.
        """
            i_should_continue = True
            while (i_should_continue):
                i = input("Gmail: ")
                args = i.split()
                if len(args) == 0:
                    self.help(gmail)
                else:
                    {"recent": self.recent,
                       "list": self.list,
                       "read": self.read,
                       "back": self.back}.get(args[0], self.help)(args)
            print("Gmail client closing...")
            if self.gmail.close():
                print("YES TODO")
                return True
            else:
                print("SHIT")
                return False

    def _command_pattern(self, args: List[str]) -> bool:
        """ The function pattern for user commands to follow.

        Args:
            args: User specified inputs such that args[0] is the command
                name itself.

        Return:
            True, if the use input was able to be processed, False otherwise.
        """
        _logger.warning(
            f"_command_pattern is the design pattern. It is an interface that"
            f"should not be called. Args: {args}"
        )
        return False

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
        self.gmail.process_email_list("category:primary",
                                      max_messages=number)

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
                "Please provide a query with this command. I.e. `list 'category:primary'`")
        else:
            query = args[1]
            messages = self.gmail.get_messages_from_query(query, max_messages=None if len(
                args) < 3 else args[2])
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

            except ValueError as e:
                print(f"The value {args[1]} is not an integer.")
                return False

            except IndexError as e:
                print(f"Index greater than number of messages. {index}>={len(self.messages)}")
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", default=0, action="count", help="verbosity")
    parser.add_argument("--credentials", "-c", default=False, help="Gmail credentials to use when authenticating with Gmail API.")
    args = parser.parse_args()
    logging.set_severity_from_verbosity(args.verbose)
    
    if args.credentials:
      gmail = GmailHandler(DEFAULT_CREDENTIAL_PATH)

    elif os.path.exists(DEFAULT_CREDENTIAL_PATH):
      gmail = GmailHandler(DEFAULT_CREDENTIAL_PATH)
    else:
        print("No credentials were passed in and there were no default credentials set. Cannot run.")
        exit(1)

    controller = GmailController(gmail)
    controller.run()
