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
    command = sys.argv[1]
    if command == 'expense' or command == 'income':
        print("Attempting to insert new", command, "entry:")
    else:
        print("ERROR: Invalid command. Valid commands are 'expense' and 'income'.")
        sys.exit(0)
    entry = sys.argv[2].split(',')
    if len(entry) is 4:
        print("Date:", entry[0], "\nAmount:", entry[1], "\nDescription:", entry[2], "\nCategory:", entry[3], "\n")
    else:
        print("ERROR: Invalid number of fields.")
        sys.exit(0)

    # authorize
    shutil.copyfile(GLOBAL_TOKEN_PATH, 'token.json')
    store = file.Storage('token.json')
    creds = store.get()
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    print("Authorization successful.")

    # fetch existing transactions
    rangeName = 'Transactions!C5:C74' if command == 'expense' else 'Transactions!H5:H74'
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=rangeName).execute()
    values = result.get('values', [])

    # find the index of the last entry
    index = 5
    if values:
        index += len(values)

    # add new entry
    startCol = "B" if command == 'expense' else "G"
    endCol = "E" if command == 'expense' else "J"
    rangeName = "Transactions!" + startCol + str(index) + ":" + endCol + str(index)
    body = {'values': [entry]}
    result = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=rangeName,
                                                    valueInputOption="USER_ENTERED", body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))
    os.remove('token.json')
