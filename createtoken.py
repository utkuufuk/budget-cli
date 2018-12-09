from oauth2client import file, client, tools
from httplib2 import Http
from googleapiclient.discovery import build

store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    scopes = 'https://www.googleapis.com/auth/spreadsheets'
    flow = client.flow_from_clientsecrets('credentials.json', scopes)
    tools.run_flow(flow, store)
