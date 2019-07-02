import json 
import email
import base64
import os
from typing import List

from oauth2client.file import Storage
from apiclient.discovery import build
import html2text
import time

DEFAULT_CREDENTIAL_PATH="credentials-je.dat"
class CommandHandler(object):

    def __init__(self, gmail):
        self.gmail = gmail

    def recent(self, args):
        number = 10 if len(args) < 2 else args[1]
        number = int(number)
        self.gmail.process_email_list("category:primary", max_messages=number)

    def list(self, args):
        if len(args) < 2:
            print("Please provide query with this command. I.e. `list 'category:primary'`")
        else:
            query = args[1]
            self.gmail.process_email_list(query, max_messages=None if len(args)< 3 else args[2])

    def read(self, args):
        if len(args) < 2:
            print("Please provide the index of email to read.")
        else:
            try:
                number = int(args[1])
                self.gmail.read_message(number)

            except ValueError as e:
                print(f"The value {args[1]} is not an integer.")

            except IndexError as e:
                print(f"Index {number} is out of range.")

    def back(self, args):
        self.gmail.print_previous_list()


    def help(self, gmail):
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



class GmailHandler(object): 
    
    def __init__(self, cred_file):
        self.cred = Storage(cred_file).get()
        self.service = build('gmail', 'v1', credentials=self.cred)
        self.message_list = []

    def get_message_from_id(self, id:str, form:str="raw", metadata:List[str]=None):
        """ Gets a Message object, given its ID.

        :param id: Id of a email.
        :param form: The format of email to return, options are: 'full', 'metadata', 'minimal', 'raw'.
                        See https://developers.google.com/gmail/api/v1/reference/users/messages/get
        :return: A Message Object.
        """
        if metadata:
            return self.service.users().messages().get(userId="me", id=id, format=form, metadataHeaders=metadata).execute()
        else:
            return self.service.users().messages().get(userId="me", id=id, format=form).execute()

    def process_email_list(self, query:str, max_messages:int=None):
        """ Prints the snippets for a set of emails, following a given query.

        :param query: A query string to filter emails with. Same format as string
            filtering in the gmail GUI.
        :param max_messages: The maximum amount of messages to retrieve and print.
        """
        messages = self.get_messages_from_query(query, form="metadata", metadata=["From", "Message-ID"], max_messages=max_messages)

        self.message_list = messages
        print(f"## Emails from Query: `{query}`")
        self.print_previous_list()
        if max_messages:
            print(f"NOTE: Only the top {max_messages} messages were retrieved. There may be more.")

    def print_previous_list(self):
        for m, i in zip(self.message_list, range(len(self.message_list))):
            From = m["payload"]["headers"]
            From = next(x["value"] for x in From if x["name"] == "From")
            From = f"{(45-len(From))*' '}{From}"
            index = f"{((len(self.message_list)//10)-(i//10))*' '}{i}"
            print(f"|{index}|{From} | {m['snippet'][:140]} ")

    def get_messages_from_query(self, query, form:str="raw", metadata:List[str]=None, max_messages:int=None)->None:
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
        messages = self.service.users().messages().list(userId="me", q=query).execute()
        if max_messages:
            return [self.get_message_from_id(m["id"], form=form, metadata=metadata) for m in messages["messages"][0:max_messages]]
        else:
            return [self.get_message_from_id(m["id"], form=form, metadata=metadata) for m in messages["messages"]]
        
    def read_message(self, index:int)->None:
        """ Given an index, prints the corresponding message from the previous list.

        :param index: The index of email from the previously queried list.
        """
        if index >= len(self.message_list):
            raise IndexError()

        else:
            message = self.get_message_from_id(self.message_list[index]["id"])
            self.print_message(message)

    def print_message(self, message)->None:
        """ Prints a single email.

        :param message: A gmail Message object.
        """
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

    @staticmethod
    def run():
        """Handles interactions with the gmail handler, including
            authentication and email retrieval.

        """
        if os.path.exists(DEFAULT_CREDENTIAL_PATH):
            gmail = GmailHandler(DEFAULT_CREDENTIAL_PATH)
            commands = CommandHandler(gmail)

            should_continue = True
            while(should_continue):
                i = input("Gmail: ")
                args = i.split()
                if len(args) == 0:
                    commands.help(gmail)
                else:
                    {"recent": commands.recent, 
                     "list": commands.list, 
                     "read": commands.read,
                     "back": commands.back}.get(args[0], commands.help)(args)
        else:
            print(f"Credentials not at default path: {DEFAULT_CREDENTIAL_PATH}.")
            print("Will require web login.")
            raise NotImplementedError("Need to integrate web auth script into CLI")
            

if __name__ == '__main__':
    GmailHandler.run()
    
