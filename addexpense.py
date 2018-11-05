#!/usr/bin/env python3
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from pathlib import Path
import sys
import os
import shutil

# replace this with your spreadsheet ID
SPREADSHEET_ID = '1jANO8_sbQ5pLEAJbyxWcQiklPboPtSp8ijrp_RTD0Aw'
GLOBAL_TOKEN_PATH = str(Path.home()) + '/.local/share/token.json'

if __name__ == '__main__':
    # validate input
    entry = sys.argv[1].split(',')
    if len(entry) is 4:
        print("Date:", entry[0], "\nCost:", entry[1], "\nDesc:", entry[2], "\nType:", entry[3], "\n")
    else:
        print("Invalid number of fields. Aborting.")
        sys.exit(0)

    # authorize
    shutil.copyfile(GLOBAL_TOKEN_PATH, 'token.json')
    store = file.Storage('token.json')
    creds = store.get()
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    print("Authorization successful.")

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
    body = {'values': [entry]}
    result = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=rangeName,
                                                    valueInputOption="USER_ENTERED", body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))
    os.remove('token.json')
