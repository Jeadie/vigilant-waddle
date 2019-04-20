from oauth2client.file import Storage
from apiclient.discovery import build

class GmailHandler(object): 
    
    def __init__(self, cred_file):
        self.cred = Storage(cred_file).get()
        self.service = build('gmail', 'v1', credentials=self.cred)

if __name__ == '__main__':
    a = GmailHandler("credentials-j.dat")
    print(a.cred, a.service)
    