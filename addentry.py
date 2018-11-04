from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import argparse

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
SPREADSHEET_ID = '1jANO8_sbQ5pLEAJbyxWcQiklPboPtSp8ijrp_RTD0Aw'

if __name__ == '__main__':
    # parse program arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=str, help='transaction date')
    parser.add_argument('--cost', type=int, help='transaction amount')
    parser.add_argument('--desc', type=str, help='transaction description')
    parser.add_argument('--type', type=str, help='transaction type')
    args = parser.parse_args()

    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # call the sheets API
    rangeName = 'Transactions!C5:C74'
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=rangeName).execute()
    values = result.get('values', [])

    # iterate down to the last entry
    index = 5
    if values:
        index += len(values)

    # add new entry
    rangeName = "Transactions!B" + str(index) + ":E" + str(index)
    entry = [[args.date, args.cost, args.desc, args.type]]
    body = {'values': entry}
    result = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=rangeName,
                                                    valueInputOption="USER_ENTERED", body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))
