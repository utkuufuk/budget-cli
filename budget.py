#!/usr/bin/env python3
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib2 import Http
from oauth2client import file, client, tools
from pathlib import Path
import sys
import os
import datetime
import json

APP_DIR = str(Path.home()) + '/.config/budget-cli/'
CONFIG_FILE_PATH = APP_DIR + 'config.json'
MONTHLY_ID_KEY = 'monthly-budget-id'
ANNUAL_ID_KEY = 'annual-budget-id'
NUM_EXPENSE_CATEGORIES_KEY = 'num-expense-categories'
NUM_INCOME_CATEGORIES_KEY = 'num-income-categories'
MAX_ROWS_KEY = 'max-rows'
MONTH_COLS = {'Jan':'D', 'Feb':'E', 'Mar':'F', 'Apr':'G', 'May':'H', 'Jun':'I',
              'Jul':'J', 'Aug':'K', 'Sep':'L', 'Oct':'M', 'Nov':'N', 'Dec':'O'}
COMMANDS = ['mid', 'aid', 'murl', 'aurl', 'summary', 'log', 'sync', 'expense', 'income']

# writes configuration to file
def saveConfig(config):
    with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    sys.exit(0)

# extracts the ID of a spreadsheet from its URL
def extractId(url):
    start = url.find("spreadsheets/d/")
    end = url.find("/edit#")
    if start == -1 or end == -1:
        print("Invalid URL:", url, file=sys.stderr)
        sys.exit(1)
    return arg[(start + 15):end]

# reads MxN cells from a spreadsheet
def readCells(service, ssheetId, rangeName):
    try:
        return service.spreadsheets().values().get(spreadsheetId=ssheetId, range=rangeName).execute().get('values', [])
    except HttpError:
        print("HTTP Error. Spreadsheet ID might be invalid:", ssheetId, file=sys.stderr)
        sys.exit(1)

# writes MxN cells into a spreadsheet
def writeCells(service, ssheetId, rangeName, values):
    return service.spreadsheets().values().update(spreadsheetId=ssheetId, range=rangeName,
                                                  valueInputOption="USER_ENTERED", body={'values': values}).execute()

# copies monthly budget information to annual budget
def syncAnnual(service, annualId, sheetName, dictionary, monthCol, numCategories, maxRows):
    count = 0
    rangeName = sheetName + '!C4:C' + str(maxRows)
    keys = readCells(service, annualId, rangeName)
    for row in range(0, maxRows):
        if keys[row] and keys[row][0] in dictionary.keys():
            rangeName = sheetName + '!' + monthCol + str(4 + row)
            writeCells(service, annualId, rangeName, [[dictionary[keys[row][0]]]])
            count += 1
            if count == numCategories:
                break

# prints entries on the terminal as a table
def logEntries(entries, header):
    print("\n" + header + ":\n=============================================================================")
    for cols in entries:
        print("{0:>12s} {1:>10s}    {2:<35s} {3:<15s}".format(cols[0], cols[1], cols[2], cols[3]))

if __name__ == '__main__':
    # read command, arguments, and configuration
    cmd = sys.argv[1]
    arg = None if len(sys.argv) == 2 else sys.argv[2]
    try:
        config = json.load(open(CONFIG_FILE_PATH))
    except FileNotFoundError:
        print('Configuration file not found.', file=sys.stderr)
        sys.exit(1)

    # set monthly/annual spreadsheet ID by URL
    if cmd == 'murl' or cmd == 'aurl':
        ssheetId = extractId(arg)
        config[MONTHLY_ID_KEY if cmd == 'murl' else ANNUAL_ID_KEY] = ssheetId
        print(("Monthly" if cmd == 'murl' else "Annual") + " Budget Spreadsheet ID:", ssheetId)
        saveConfig(config)
        sys.exit(0)

    # print/set monthly/annual spreadsheet ID
    if cmd == 'mid' or cmd == 'aid':
        key = MONTHLY_ID_KEY if cmd == 'mid' else ANNUAL_ID_KEY
        if arg != None:
            config[key] = arg
            saveConfig(config)
        print(("Monthly" if cmd == 'mid' else "Annual") + " Budget Spreadsheet ID:", config[key])
        sys.exit(0)

    # temporarily change working directory to read token.json & authorize
    initialDir = os.getcwd()
    os.chdir(APP_DIR)
    store = file.Storage('token.json')
    creds = store.get()
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    os.chdir(initialDir)

    # read Summary page contents of monthly budget spreadsheet
    ssheetId = config[MONTHLY_ID_KEY]
    summary = readCells(service, ssheetId, 'Summary!B8:K' + str(27 + config[NUM_EXPENSE_CATEGORIES_KEY]))
    title = summary[0][0]

    # print monthly budget summary
    if cmd == 'summary':
        print("\n" + title + "\n=======================")
        print("Total Expenses:{0:>8s}\nTotal Income:  {1:>8s}".format(summary[14][1], summary[14][7]))
        sys.exit(0)

    # log monthly budget transaction history
    if cmd == 'log':
        logEntries(expenses, "EXPENSES")
        logEntries(income, "INCOME")
        sys.exit(0)

    # get the category map of both expenses & income from monthly budget summary
    expenses = {summary[row][0]:summary[row][3] for row in range(20, 20 + config[NUM_EXPENSE_CATEGORIES_KEY])}
    income = {summary[row][6]:summary[row][9] for row in range(20, 20 + config[NUM_INCOME_CATEGORIES_KEY])}

    # update annual budget with monthly expenses & income
    if cmd == 'sync':
        print("Synchronizing annual budget with from ", title, "expenses.")
        syncAnnual(service, config[ANNUAL_ID_KEY], 'Expenses', expenses, MONTH_COLS[title[:3]],
                   config[NUM_EXPENSE_CATEGORIES_KEY], config[MAX_ROWS_KEY])
        print("Synchronizing annual budget with from ", title, "income.")
        syncAnnual(service, config[ANNUAL_ID_KEY], 'Income', income, MONTH_COLS[title[:3]],
                   config[NUM_INCOME_CATEGORIES_KEY], config[MAX_ROWS_KEY])
        print("Annual budget succcessfully synchronized.")
        sys.exit(0)

    # insert new transaction
    if cmd == 'expense' or cmd == 'income':
        # remove any leading & trailing whitespace from transaction arguments and validate
        entry = [e.strip() for e in arg.split(',')]

        # validate number of arguments
        if len(entry) != 3 and len(entry) != 4:
            print("Invalid number of fields in transaction.", file=sys.stderr)
            sys.exit(1)

        # automatically assign today if only 3 arguments are specified
        if len(entry) is 3:
            print("Only 3 fields were specified. Assigning today to date field.")
            now = datetime.datetime.now()
            entry.insert(0, str(now)[:10])

        # reject transaction if amount is invalid
        if int(entry[1]) <= 0 or int(entry[1]) > 99999:
            print("Invalid transaction amount:", entry[1], file=sys.stderr)
            sys.exit(1)

        # reject transaction if category is invalid 
        categories = expenses.keys() if cmd == 'expense' else income.keys()
        if entry[3] not in categories:
            print("Invalid category:", entry[3], "\nValid categories are:", file=sys.stderr)
            for key in categories:
                print(key)
            sys.exit(1)

        # find row index of last transaction by reading existing expense/income entries
        rangeName = 'Transactions!G5:J' if cmd == 'income' else 'Transactions!B5:E'
        entries = readCells(service, ssheetId, rangeName + str(config[MAX_ROWS_KEY]))
        rowIdx = 5 if not entries else 5 + len(entries)

        # update cells
        startCol = "B" if cmd == 'expense' else "G"
        endCol = "E" if cmd == 'expense' else "J"
        rangeName = "Transactions!" + startCol + str(rowIdx) + ":" + endCol + str(rowIdx)
        result = writeCells(service, ssheetId, rangeName, [entry])
        print('{0} cells successfully updated in {1} spreadsheet.'.format(result.get('updatedCells'), title))
        sys.exit(0)

    print("Invalid command. Valid commands are:", COMMANDS, file=sys.stderr)
