#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path
from httplib2 import Http
from datetime import datetime
from oauth2client import file
from collections import namedtuple
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

APP_DIR = str(Path.home()) + '/.budget-cli/'
CONFIG_FILE_PATH = APP_DIR + 'config.json'
MONTHLY_ID_KEY = 'monthly-budget-id'
ANNUAL_ID_KEY = 'annual-budget-id'
MAX_ROWS = 1000
NUM_TRANSACTION_FIELDS = 4
FIRST_TRANSACTION_ROW = 5
MONTH_COLS = {'Jan':'D', 'Feb':'E', 'Mar':'F', 'Apr':'G', 'May':'H', 'Jun':'I',
              'Jul':'J', 'Aug':'K', 'Sep':'L', 'Oct':'M', 'Nov':'N', 'Dec':'O'}
COMMAND_SET = ['murl', 'aurl', 'summary', 'categories', 'log', 'sync', 'expense', 'income']

Summary = namedtuple('Summary', 'cells, title, categories')
Arguments = namedtuple('Arguments', 'command, params, monthlySheetId, annualSheetId')

# extracts the ID of a spreadsheet from its URL
def extractId(url):
    start = url.find("spreadsheets/d/")
    end = url.find("/edit#")
    if start == -1 or end == -1:
        print("Invalid URL:", url, file=sys.stderr)
        sys.exit(1)
    return url[(start + 15):end]

# reads MxN cells from a spreadsheet
def readCells(service, ssheetId, rangeName):
    try:
        return service.get(spreadsheetId=ssheetId, range=rangeName).execute().get('values', [])
    except HttpError:
        print("Monthly spreadsheet ID might be invalid:", ssheetId, file=sys.stderr)
        print("Set it using the following command:\nbudget murl <SPREADSHEET_ID>", file=sys.stderr)
        sys.exit(1)

# writes MxN cells into a spreadsheet
def writeCells(service, ssheetId, rangeName, values):
    body = {'values': values}
    return service.update(
        spreadsheetId=ssheetId, range=rangeName,
        valueInputOption="USER_ENTERED", body=body).execute()

# inserts a new expense/income transaction to monthly budget spreadsheet
def insertTransaction(transaction, command, service, ssheetId, rowIdx):
    startCol = "B" if command == 'expense' else "G"
    endCol = "E" if command == 'expense' else "J"
    rangeName = "Transactions!" + startCol + str(rowIdx) + ":" + endCol + str(rowIdx)
    return writeCells(service, ssheetId, rangeName, [transaction])

# checks if the input transaction is valid or not
def isValid(transaction, categories):
    try:
        if len(transaction) != NUM_TRANSACTION_FIELDS:
            raise UserWarning("Invalid number of fields in transaction.")
        try:
            if float(transaction[1]) <= 0 or float(transaction[1]) > 99999:
                raise UserWarning("Invalid transaction amount: {0}".format(transaction[1]))
        except ValueError as e:
                raise UserWarning("Invalid transaction amount: {0}".format(transaction[1]))
        if transaction[3] not in categories.keys():
            message = "Invalid category: {0}. Valid categories are:".format(transaction[3])
            for key in categories:
                message += "\n" + key
            raise UserWarning(message)
    except UserWarning as e:
        print(str(e), "\n", file=sys.stderr)
        return False
    return True

# synchronizes annual budget with monthly budget data
def sync(service, ssheetId, sheetName, title, categories):
    rangeName = sheetName + '!C4:C' + str(MAX_ROWS)
    keys = readCells(service, ssheetId, rangeName)
    count = 0
    print("\nSynchronizing annual budget with", title, sheetName + ":\n")
    for row in range(0, MAX_ROWS):
        if keys[row] and keys[row][0] in categories.keys():
            rangeName = sheetName + '!' + MONTH_COLS[title[:3]] + str(4 + row)
            writeCells(service, ssheetId, rangeName, [[categories[keys[row][0]]]])
            print("{0:<22s} {1:>6s}".format(keys[row][0], categories[keys[row][0]]))
            count += 1
            if count == len(categories):
                break
    print("\n{0} succcessfully synchronized in annual budget.".format(title))

# lists categories & amounts in a two-column list
def listCategories(dictionary, header):
    printHeader(header, 68)
    newline = True
    for category, amount in dictionary.items():
        if newline:
            print("{0:<22s} {1:>6s}          ".format(category, amount), end='')
            newline = False
        else:
            print("{0:<22s} {1:>6s}".format(category, amount))
            newline = True
    print()

# prints the header followed by a dash with desired length
def printHeader(title, length):
    print("\n" + title)
    for i in range(0, length):
        print("=") if i == length - 1 else print("=", end="")

# reads Summary page of the monthly budget & get the number of expense/income categories
def readSummaryPage(service, ssheetId):
    cells = readCells(service, ssheetId, 'Summary!B8:K' + str(MAX_ROWS))
    numIncomeCategories = len([r for r in range(20, len(cells)) if len(cells[r]) == 10])
    incomeCategories = {cells[row][6]:cells[row][9] for row in range(20, 20 + numIncomeCategories)}
    expenseCategories = {cells[row][0]:cells[row][3] for row in range(20, len(cells))}
    return Summary(cells, cells[0][0], {'income':incomeCategories, 'expense':expenseCategories})

# prints entries on the terminal as a table
def logTransactions(entries, header):
    printHeader(header, 79)
    for rows in entries:
        print("{0:>12s} {1:>12s}    {2:<35s} {3:<15s}".format(rows[0], rows[1], rows[2], rows[3]))

# reads expense & income transactions from monthly budget
def readTransactions(service, ssheetId, type):
    rangeName = ('Transactions!B5:E' if type == "expense" else 'Transactions!G5:J') + str(MAX_ROWS)
    return readCells(service, ssheetId, rangeName)

# authorize & build spreadsheet service
def getSheetService():
    os.chdir(APP_DIR)
    store = file.Storage('token.json')
    creds = store.get()
    return build('sheets', 'v4', http=creds.authorize(Http())).spreadsheets().values()

# save monthly/annual spreadsheet ID in configuration file
def setSheetId(args):
    ssheetId = extractId(args.params)
    config = {MONTHLY_ID_KEY: args.monthlySheetId, ANNUAL_ID_KEY: args.annualSheetId}
    config[MONTHLY_ID_KEY if args.command == 'murl' else ANNUAL_ID_KEY] = ssheetId
    print(("Monthly" if args.command == 'murl' else "Annual") + " Budget Spreadsheet ID:", ssheetId)
    with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# reads program arguments & configuration
def readArgs():
    try:
        params = None if len(sys.argv) == 2 else sys.argv[2]
        config = json.load(open(CONFIG_FILE_PATH))
        return Arguments(sys.argv[1], params, config[MONTHLY_ID_KEY], config[ANNUAL_ID_KEY])
    except FileNotFoundError:
        print('Configuration file moved or deleted: {0}'.format(CONFIG_FILE_PATH), file=sys.stderr)
        sys.exit(1)

def main():
    args = readArgs()
    if args.command in ('murl', 'aurl'):
        setSheetId(args)
        return
    service = getSheetService()
    if args.command == 'log':
        expenses = readTransactions(service, args.monthlySheetId, "expense")
        income = readTransactions(service, args.monthlySheetId, "income")
        logTransactions(expenses, "EXPENSES")
        logTransactions(income, "INCOME")
        return
    summary = readSummaryPage(service, args.monthlySheetId)
    if args.command == 'summary':
        printHeader(summary.title, 16)
        print("Expenses:{0:>7s}\nIncome:{1:>9s}".format(summary.cells[14][1], summary.cells[14][7]))
    elif args.command == 'categories':
        listCategories(summary.categories['expense'], "EXPENSES")
        listCategories(summary.categories['income'], "INCOME")
    elif args.command == 'sync':
        sync(service, args.annualSheetId, 'Expenses', summary.title, summary.categories['expense'])
        sync(service, args.annualSheetId, 'Income', summary.title, summary.categories['income'])
    elif args.command in ('expense', 'income'):
        transaction = [e.strip() for e in args.params.split(',')]
        if len(transaction) is 3:
            print("Only 3 fields were specified. Assigning today to date field.")
            transaction.insert(0, str(datetime.now())[:10])
        if isValid(transaction, summary.categories[args.command]):
            transactions = readTransactions(service, args.monthlySheetId, args.command)
            rowIdx = FIRST_TRANSACTION_ROW + (0 if not transactions else len(transactions))
            insertTransaction(transaction, args.command, service, args.monthlySheetId, rowIdx)
            print('Transaction inserted in {0} budget:\n{1}'.format(summary.title, transaction))
    else:
        print("Invalid command. Valid commands are:", COMMAND_SET, file=sys.stderr)

if __name__ == '__main__':
    main()
