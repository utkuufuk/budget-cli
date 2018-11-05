#!/usr/bin/env python3
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib2 import Http
from oauth2client import file, client, tools
from pathlib import Path
import sys
import os
import shutil

GLOBAL_TOKEN_PATH = str(Path.home()) + '/.local/share/google-budget/token.json'
SPREADSHEET_ID_PATH = str(Path.home()) + '/.local/share/google-budget/spreadsheet.id'

if __name__ == '__main__':
    # validate command
    command = sys.argv[1]
    if command == 'expense' or command == 'income':
        print("Attempting to insert new", command, "transaction:")
    elif command == 'sheet':
        # write spreadsheet ID
        with open(SPREADSHEET_ID_PATH, 'w') as f:
            f.write(sys.argv[2])
        print("Spreadsheet ID has been set:", sys.argv[2])
        sys.exit(0)
    else:
        print("Invalid command. Valid commands are 'sheet', 'expense' and 'income'.", file=sys.stderr)
        sys.exit(1)

    # validate transaction
    entry = sys.argv[2].split(',')
    if len(entry) is 4:
        print("Date:", entry[0], "\nAmount:", entry[1], "\nDescription:", entry[2], "\nCategory:", entry[3], "\n")
    else:
        print("Invalid number of fields in transaction.", file=sys.stderr)
        sys.exit(1)

    # read spreadsheet ID
    try:
        with open(SPREADSHEET_ID_PATH) as f:
            ssheetId = f.read()
    except:
        print("Spreadsheet ID not found. Set your spreadsheet ID with the following command:", file=sys.stderr)
        print("budget sheet <spreadsheet_id>", file=sys.stderr)
        sys.exit(1)

    # temporarily copy the auth token into current dir and authorize
    shutil.copyfile(GLOBAL_TOKEN_PATH, 'token.json')
    store = file.Storage('token.json')
    creds = store.get()
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    print("Authorization successful.")

    # fetch existing data in order to find the index of the last transaction
    try:
        rangeName = 'Transactions!C5:C74' if command == 'expense' else 'Transactions!H5:H74'
        result = service.spreadsheets().values().get(spreadsheetId=ssheetId, range=rangeName).execute()
        values = result.get('values', [])
        index = 5
        if values:
            index += len(values)
    except HttpError:
        print("Invalid spreadsheet ID. Set your spreadsheet ID with the following command:", file=sys.stderr)
        print("budget sheet <spreadsheet_id>", file=sys.stderr)
        sys.exit(1)

    # add new transaction
    startCol = "B" if command == 'expense' else "G"
    endCol = "E" if command == 'expense' else "J"
    rangeName = "Transactions!" + startCol + str(index) + ":" + endCol + str(index)
    body = {'values': [entry]}
    result = service.spreadsheets().values().update(spreadsheetId=ssheetId, range=rangeName,
                                                    valueInputOption="USER_ENTERED", body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))
    os.remove('token.json')
