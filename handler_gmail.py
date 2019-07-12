import base64
import email
import json
import logging
from typing import List, Dict

from oauth2client.file import Storage
from apiclient.discovery import build
import html2text

from exceptions import NotAuthenticatedError

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
        # TODO: Allow for credentials as service account keys
        #  (as GOOGLE_APPLICATION_CREDENTIALS)
        self.cred = Storage(cred_file).get()
        self.service = build("gmail", "v1", credentials=self.cred)

    def close(self) -> bool:
        """ Closes down the connection with the API.

        After an instance calls this method, it is essentially unusable.

        Returns:
            True if Gmail connection was properly ended, False otherwise.
        """
        # TODO: investigate closing down gmail.
        return True

    def get_current_email(self) -> str:
        """ Gets the email address currently authenticated.

        Returns:
            The email address currently authenticated.

        Raises:
            NotAuthenticatedError: If the service handler is not authenticated.

        """
        try:
            return json.loads(self.cred.to_json())["id_token"]["email"]
        except KeyError:
            _logger.warning(
                f"Error occured with credentials. No key `email` in JSON"
                f"credentials."
            )
        except ValueError as e:
            _logger.warning(
                f"Error occured decoding credentials JSON. Error: {e}."
            )

        raise NotAuthenticatedError("")

    def get_message_from_id(
        self, id: str, form: str = "raw", metadata: List[str] = None
    ) -> Dict[str, str]:
        """ Gets a Message object, given its ID.

        Args:
            id: Id of a email.
            form: The format of email to return, options are:
                    'full', 'metadata', 'minimal', 'raw'.

            metadata: metadata headers to include when receiving messages.

        Returns:
            A message Object.

        Raises:
            TBD
        """
        if metadata:
            return (
                self.service.users()
                .messages()
                .get(
                    userId="me", id=id, format=form, metadataHeaders=metadata
                )
                .execute()
            )
        else:
            return (
                self.service.users()
                .messages()
                .get(userId="me", id=id, format=form)
                .execute()
            )

    def print_email_list(self, emails):
        """ Prints a list of email previews, including the name of the sender
            and a snippet of the message.

        Args:
            emails: A list of message objects from the Gmail API.

        Return:
            True if the list of emails was successfully sent to stdout,
            False otherwise.
        """
        try:
            for m, i in zip(emails, range(len(emails))):
                From = m["payload"]["headers"]
                From = next(x["value"] for x in From if x["name"] == "From")
                From = f"{(45 - len(From)) * ' '}{From[:45]}"
                index = f"{((len(emails) // 10) - (i // 10)) * ' '}{i}"
                print(f"|{index}|{From} | {m['snippet'][:140]} ")
        except KeyError as e:
            _logger.error(
                f"An Gmail message object did not have expected keys."
                f" Error: {e}."
            )
            return False
        else:
            return True

    def get_messages_from_query(
        self,
        query,
        form: str = "raw",
        metadata: List[str] = None,
        max_messages: int = None,
    ) -> List[Dict[str, str]]:
        """ Returns complete message objects for a single query.

        Args:
            query: A query string to filter emails with. Same format as
                string filtering in the gmail GUI.
            form: The form of email to return, options are:
                    'full', 'metadata', 'minimal', 'raw'.

            max_messages: The maximum number of messages to retrieve from
                             gmail servers. If not set, all messages matching
                             the filter will be returned.

        Returns: A list of Message objects filtered by the given query.
        """
        messages = (
            self.service.users()
            .messages()
            .list(userId="me", q=query)
            .execute()
        )
        if max_messages:
            return [
                self.get_message_from_id(
                    m["id"], form=form, metadata=metadata
                )
                for m in messages["messages"][0:max_messages]
            ]
        else:
            return [
                self.get_message_from_id(
                    m["id"], form=form, metadata=metadata
                )
                for m in messages["messages"]
            ]

    def read_message(self, message: Dict[str, str]) -> bool:
        """ Given an index, prints the corresponding message
            from the previous list.

        Args:
            message: the message object to be printed, in detail with

        Returns:
            True, if it was successful in displaying the email.
            False otherwise.

        """
        # TODO: Think of a better way to represent individual emails.
        #  The current, dumps the html out to stdout.
        # Ideas:
        #   Render in browser, pop-up.
        #   Filter html tags.
        msg_str = base64.urlsafe_b64decode(message["raw"].encode("ASCII"))

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
