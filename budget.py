#!/usr/bin/env python3
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib2 import Http
from oauth2client import file, client, tools
from pathlib import Path
import sys
import os
import datetime

APP_DIR = str(Path.home()) + '/.local/share/budget-cli/'
SPREADSHEET_ID_PATH = APP_DIR + 'spreadsheet.id'

if __name__ == '__main__':
    command = sys.argv[1]
    arg = sys.argv[2]

    # validate URL
    if command == 'url': 
        start = arg.find("spreadsheets/d/")
        end = arg.find("/edit#")
        if start == -1 or end == -1:
            print("Invalid URL:", arg, file=sys.stderr)
            sys.exit(1)

    # write spreadsheet ID & exit if command is 'id' or 'url'
    if command == 'id' or command == 'url':
        ssheetId = arg if command == 'id' else arg[(start + 15):end]
        with open(SPREADSHEET_ID_PATH, 'w') as f:
            f.write(ssheetId)
        print("Spreadsheet ID has been set:", ssheetId)
        sys.exit(0)

    # exit if command is invalid
    if command != 'expense' and command != 'income':
        print("Invalid command:", command, "\nValid commands are 'id', 'url', 'expense' and 'income'.", file=sys.stderr)
        sys.exit(1)

    # validate transaction if command is 'expense' or 'income'
    entry = arg.split(',')
    if len(entry) != 3 and len(entry) != 4:
        print("Invalid number of fields in transaction.", file=sys.stderr)
        sys.exit(1)
    if len(entry) is 3:
        print("Only 3 fields were specified. Assigning today to date field.")
        now = datetime.datetime.now()
        entry.insert(0, str(now)[:10])
    print("Date:", entry[0], "\nAmount:", entry[1], "\nDescription:", entry[2], "\nCategory:", entry[3], "\n")

    # read spreadsheet ID from file
    try:
        with open(SPREADSHEET_ID_PATH) as f:
            ssheetId = f.read()
    except:
        print("Spreadsheet ID not found. Set your spreadsheet ID with one of the following commands:", file=sys.stderr)
        print("budget id <SPREADSHEET_ID>\nbudget url <SPREADSHEET_URL>", file=sys.stderr)
        sys.exit(1)

    # temporarily change working directory to read token.json & authorize
    initialDir = os.getcwd()
    os.chdir(APP_DIR)
    store = file.Storage('token.json')
    creds = store.get()
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    print("Authorization successful.")
    os.chdir(initialDir)

    # fetch existing data in order to find the row index of the last transaction
    try:
        rangeName = 'Transactions!C5:C74' if command == 'expense' else 'Transactions!H5:H74'
        result = service.spreadsheets().values().get(spreadsheetId=ssheetId, range=rangeName).execute()
        values = result.get('values', [])
        rowIdx = 5 if not values else 5 + len(values)
    except HttpError:
        print("Invalid spreadsheet ID: " + ssheetId, file=sys.stderr)
        print("Set your spreadsheet ID with the following command:\nbudget sheet <spreadsheet_id>", file=sys.stderr)
        sys.exit(1)

    # add new transaction
    startCol = "B" if command == 'expense' else "G"
    endCol = "E" if command == 'expense' else "J"
    rangeName = "Transactions!" + startCol + str(rowIdx) + ":" + endCol + str(rowIdx)
    body = {'values': [entry]}
    result = service.spreadsheets().values().update(spreadsheetId=ssheetId, range=rangeName,
                                                    valueInputOption="USER_ENTERED", body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))
