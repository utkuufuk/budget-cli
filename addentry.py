#!/usr/bin/env python3
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import sys

# if modifying these scopes, delete the file token.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
SPREADSHEET_ID = '1jANO8_sbQ5pLEAJbyxWcQiklPboPtSp8ijrp_RTD0Aw'

if __name__ == '__main__':
    # validate input
    transaction = sys.argv[1].split(',')
    if len(transaction) is 4:
        print("Transaction:", transaction)
    else:
        print("Invalid number of fields. Aborting.")
        sys.exit(0)

    # authenticate
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # fetch existing transactions
    rangeName = 'Transactions!C5:C74'
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=rangeName).execute()
    values = result.get('values', [])

    # find the index of the last entry
    index = 5
    if values:
        index += len(values)

    # add new entry
    rangeName = "Transactions!B" + str(index) + ":E" + str(index)
    body = {'values': [transaction]}
    result = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=rangeName,
                                                    valueInputOption="USER_ENTERED", body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))
