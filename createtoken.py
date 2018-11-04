#!/usr/bin/env python3
from oauth2client import file, client, tools
from httplib2 import Http
from googleapiclient.discovery import build

# delete 'token.json' if this is modified
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

if __name__ == '__main__':
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
