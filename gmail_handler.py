from oauth2client.file import Storage
from apiclient.discovery import build
import json 
import email
import base64
import html2text

class GmailHandler(object): 
    
    def __init__(self, cred_file):
        self.cred = Storage(cred_file).get()
        self.service = build('gmail', 'v1', credentials=self.cred)

    def get_message_from_id(self, id, raw=False):
        return self.service.users().messages().get(userId="me", id=id, format="raw" if raw else "full").execute()
        
            

    def get_snippets_from_query(self, query, return_messages=False, raw=False):
        messages = self.service.users().messages().list(userId="me", q=query).execute()
        messages = [self.get_message_from_id(m["id"], raw=raw) for m in messages["messages"]]
        snippets = [m["snippet"] for m in messages]
        if return_messages:
            return (snippets, messages)
        else:
            return snippets
    
    def print_snippets(self, snippets):
        
        for s in snippets:
            print(f" - {s}")

    def print_message(self, message):
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

        mime_msg = email.message_from_string(msg_str.decode())
        
        h = html2text.HTML2Text()
        h.ignore_links = True
        
        if mime_msg.is_multipart():
            for payload in mime_msg.get_payload():
                # if payload.is_multipart(): ...
                print(h.handle(payload.get_payload(decode=False)))
        else:
                print(h.handle(mime_msg.get_payload(decode=False)))

            

if __name__ == '__main__':
    a = GmailHandler("credentials-je.dat")
    s, m = a.get_snippets_from_query("from:cal newport", return_messages=True, raw=True)
    a.print_message(m[0])