from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# if modifying these scopes, delete the file token.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
SPREADSHEET_ID = '1jANO8_sbQ5pLEAJbyxWcQiklPboPtSp8ijrp_RTD0Aw'

if __name__ == '__main__':
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))
