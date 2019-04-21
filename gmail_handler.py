import json 
import email
import base64
import os

from oauth2client.file import Storage
from apiclient.discovery import build
import html2text

DEFAULT_CREDENTIAL_PATH="credentials-je.dat"

class GmailHandler(object): 
    
    def __init__(self, cred_file):
        self.cred = Storage(cred_file).get()
        self.service = build('gmail', 'v1', credentials=self.cred)
        self.message_list = []

    def get_message_from_id(self, id:str, raw:bool=False):
        """ Gets a Message object, given its ID.

        :param id: Id of a email.
        :param raw: If True, will return the raw email data in the 'raw' key,value.
        :return: A Message Object.
        """
        return self.service.users().messages().get(userId="me", id=id, format="raw" if raw else "full").execute()

    def process_email_list(self, query:str, max_messages:int=None):
        """ Prints the snippets for a set of emails, following a given query.

        :param query: A query string to filter emails with. Same format as string
            filtering in the gmail GUI.
        :param max_messages: The maximum amount of messages to retrieve and print.
        """
        messages = self.get_messages_from_query(query, raw=True, max_messages=max_messages)
        self.message_list = messages
        print(f"## Emails from Query: `{query}`|")
        for m, i in zip(messages, range(len(messages))):
            print(f"- {i} - {m['snippet']} ")
        if max_messages:
            print(f"NOTE: Only the top {max_messages} messages were retrieved. There may be more.")

    def print_previous_list(self):
        for m, i in zip(self.message_list, range(len(self.message_list))):
            print(f"- {i} - {m['snippet']} ")

    def get_messages_from_query(self, query, raw:bool=False, max_messages:int=None)->None:
        """ Returns complete message objects for a single query.

        :param query: A query string to filter emails with. Same format as string
            filtering in the gmail GUI.
        :param raw: If True, will return the raw email data in the 'raw' key,value.
        :param max_messages: The maximum number of messages to retrieve from
                             gmail servers. If not set, all messages matching
                             the filter will be returned.
        :return: A list of Message objects filtered by the given query.
        """
        messages = self.service.users().messages().list(userId="me", q=query).execute()
        if max_messages:
            return [self.get_message_from_id(m["id"], raw=raw) for m in messages["messages"][0:max_messages]]
        else:
            return [self.get_message_from_id(m["id"], raw=raw) for m in messages["messages"]]
        
    def read_message(self, index:int)->None:
        """ Given an index, prints the corresponding message from the previous list.

        :param index: The index of email from the previously queried list.
        """
        if index >= len(self.message_list):
            raise IndexError()

        else:
            self.print_message(self.message_list[index])

    def print_message(self, message)->None:
        """ Prints a single email.

        :param message: A gmail Message object.
        """
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

        mime_msg = email.message_from_string(msg_str.decode())
        print(f"From: {mime_msg['From']}|")
        print(f"Date: {mime_msg['Date']}|")
        h = html2text.HTML2Text()
        h.ignore_links = True
        
        if mime_msg.is_multipart():
            for payload in mime_msg.get_payload():
                print(h.handle(payload.get_payload(decode=False)))
        else:
            print(h.handle(mime_msg.get_payload(decode=False)))

    @staticmethod
    def run():
        """Handles interactions with the gmail handler, including
            authentication and email retrieval.

        """
        if os.path.exists(DEFAULT_CREDENTIAL_PATH):
            handler = GmailHandler(DEFAULT_CREDENTIAL_PATH)
            should_continue = True
            while(should_continue):
                i = input("Gmail: ")
                args = i.split()
                print(args)
                if len(args) == 0:
                    print("Not a command.")
                    continue
                if args[0] == "recent":
                    number = 10 if len(args) < 2 else args[1]
                    number = int(number)
                    handler.process_email_list("category:primary", max_messages=number)

                elif args[0] == "list":
                    if len(args) < 2:
                        print("Please provide query with this command. I.e. `list 'category:primary'`")
                    else:
                        query = args[1]
                        handler.process_email_list(query, max_messages=None if len(args)< 3 else args[2])

                elif args[0] == "read":
                    if len(args) < 2:
                        print("Please provide the index of email to read.")
                    else:
                        try:
                            number = int(args[1])
                            handler.read_message(number)

                        except ValueError as e:
                            print(f"The value {args[1]} is not an integer.")

                        except IndexError as e:
                            print(f"Index {number} is out of range.")

                elif args[0] == "back":
                    handler.print_previous_list()
                else:
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

        else:
            print(f"Credentials not at default path: {DEFAULT_CREDENTIAL_PATH}.")
            print("Will require web login.")
            raise NotImplementedError("Need to integrate web auth script into CLI")
            

if __name__ == '__main__':
    GmailHandler.run()
    