#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path
from httplib2 import Http
from datetime import datetime
from collections import namedtuple
from collections import OrderedDict
from oauth2client import file
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

APP_DIR = str(Path.home()) + '/.budget-cli/'
CONFIG_FILE_PATH = APP_DIR + 'config.json'
ANNUAL_ID_KEY = 'annual'
MAX_ROWS = 1000
NUM_TRANSACTION_FIELDS = 4
FIRST_TRANSACTION_ROW = 5
MONTH_COLS = OrderedDict([
    ('Jan','D'), ('Feb','E'), ('Mar','F'), ('Apr','G'), ('May','H'), ('Jun','I'),
    ('Jul','J'), ('Aug','K'), ('Sep','L'), ('Oct','M'), ('Nov','N'), ('Dec','O')
])
COMMAND_SET = ['summary', 'categories', 'log', 'sync', 'expense', 'income', 'edit']

Categories = namedtuple('Categories', 'expense, income')
Summary = namedtuple('Summary', 'cells, title, categories')

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
        error = "Monthly budget spreadsheet ID might be invalid. Check config file: {0}"
        raise UserWarning(error.format(CONFIG_FILE_PATH))

# writes MxN cells into a spreadsheet
def writeCells(service, ssheetId, rangeName, values):
    body = {'values': values}
    return service.update(
        spreadsheetId=ssheetId, range=rangeName,
        valueInputOption="USER_ENTERED", body=body).execute()

# inserts a new expense/income transaction to monthly budget spreadsheet
def insertTransaction(transaction, service, command, monthlySheetId, title):
    transactions = readTransactions(service, monthlySheetId, command)
    rowIdx = FIRST_TRANSACTION_ROW + (0 if not transactions else len(transactions))
    startCol = "B" if command == 'expense' else "G"
    endCol = "E" if command == 'expense' else "J"
    rangeName = "Transactions!" + startCol + str(rowIdx) + ":" + endCol + str(rowIdx)
    writeCells(service, monthlySheetId, rangeName, [transaction])
    print('Transaction inserted in {0} budget:\n{1}'.format(title, transaction))

# edits an existing income/expense transaction in monthly budget spreadsheet
def editTransaction(lineIndex, newTransaction, service, subcommand, monthlySheetId, title):
    rowIdx = FIRST_TRANSACTION_ROW + lineIndex - 1
    startCol = "B" if subcommand == 'expense' else "G"
    endCol = "E" if subcommand == 'expense' else "J"
    rangeName = "Transactions!" + startCol + str(rowIdx) + ":" + endCol + str(rowIdx)
    writeCells(service, monthlySheetId, rangeName, [newTransaction])
    print('Transaction edited in {0} budget:\n{1}'.format(title, newTransaction))

# raises a UserWarning if the line index is invalid
def validateLineIndex(lineIndex, transactions):
    if lineIndex not in range(1, len(transactions) + 1):
        raise UserWarning("Line index of {0} is invalid.".format(lineIndex))

# raises a UserWarning if the transaction is invalid
def validate(transaction, categories):
    if transaction[3] not in categories.keys():
        message = "Invalid category: {0}. Valid categories are:".format(transaction[3])
        for key in categories:
            message += "\n" + key
        raise UserWarning(message)

# parses transaction fields & inserts a date field (today) if not specified
def parseTransaction(params, editMode=False):
    dateAdded = False
    transaction = [e.strip() for e in params.split(',')]
    if len(transaction) is NUM_TRANSACTION_FIELDS - 1:
        if editMode is False:
            print("Only 3 fields were specified. Assigning today to date field.")
        transaction.insert(0, datetime.now())
        dateAdded = True
    if len(transaction) != NUM_TRANSACTION_FIELDS:
        raise UserWarning("Invalid number of fields in transaction.")
    try:
        if float(transaction[1]) <= 0 or float(transaction[1]) > 99999:
            raise ValueError()
    except ValueError:
            raise UserWarning("Invalid transaction amount: {0}".format(transaction[1]))
    return transaction, dateAdded

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
    return Summary(cells, cells[0][0], Categories(expenseCategories, incomeCategories))

# prints entries on the terminal as a table
def logTransactions(entries, header):
    index = 1
    printHeader(header, 79)
    for rows in entries:
        print("{0:>4s} {1:>12s} {2:>12s}    {3:<35s} {4:<15s}".format(str(index), rows[0], rows[1], rows[2], rows[3]))
        index += 1

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

# reads configuration from file
def readConfig():
    try:
        return json.load(open(CONFIG_FILE_PATH))
    except FileNotFoundError:
        raise UserWarning('Configuration file not found: {0}'.format(CONFIG_FILE_PATH))

# raises a UserWarning regarding an invalid month input
def raiseInvalidMonthError(date):
    error = "Invalid month: {0}\nValid months are:\n{1}"
    raise UserWarning(error.format(date, [m.lower() for m in MONTH_COLS.keys()]))

# parses transaction date & reads the corresponding monthly budget spreadsheet ID
def getMonthlySheetId(date, sheetIds):
    month = date[:3] if type(date) is str else date.strftime("%b")
    try:
        return sheetIds[month.lower()]
    except KeyError:
        raiseInvalidMonthError(month)

# reads program arguments
def readArgs():
    if sys.argv[1] not in COMMAND_SET:
        raise UserWarning("Invalid command type: Valid command types are:\n{0}".format(COMMAND_SET))
    elif sys.argv[1] in ('income', 'expense'):
        if len(sys.argv) != 3:
            raise UserWarning("Missing transaction parameters for '{0}' command.".format(sys.argv[1]))
        return sys.argv[1], sys.argv[2]
    elif sys.argv[1] == "edit":
        if sys.argv[2] not in ('income', 'expense'):
            raise UserWarning("Invalid command: Edit command has to have 'expense' or 'income' as 3rd argument.")
        if len(sys.argv) != 5:
            raise UserWarning("Invalid command: Edit command requires exactly 5 arguments.")
        return sys.argv[1], (sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        if len(sys.argv) == 3:
            month = sys.argv[2].lower()
            if month not in [m.lower() for m in MONTH_COLS.keys()]:
                raiseInvalidMonthError(month)
        else:
            month = datetime.now().strftime("%b").lower()
        return sys.argv[1], month

def main():
    try:
        sheetIds = readConfig()
        command, param = readArgs()
        service = getSheetService()
        if command in ('expense', 'income'):
            transaction, _ = parseTransaction(param)
            monthlySheetId = getMonthlySheetId(transaction[0], sheetIds)
            summary = readSummaryPage(service, monthlySheetId)
            categories = summary.categories.expense if command == 'expense' else summary.categories.income
            validate(transaction, categories)
            transaction[0] = str(transaction[0])[:10]
            insertTransaction(transaction, service, command, monthlySheetId, summary.title)
            return
        if command == "edit":
            subcommand = param[0]
            lineIndex = int(param[1])
            transaction, noExplicitDate = parseTransaction(param[2], editMode=True)
            monthlySheetId = getMonthlySheetId(transaction[0], sheetIds)
            transactions = readTransactions(service, monthlySheetId, subcommand)
            validateLineIndex(lineIndex, transactions)
            if noExplicitDate is True:
                print("Only 3 fields were specified. Assigning original date to date field.")
                transaction[0] = transactions[lineIndex - 1][0]
            summary = readSummaryPage(service, monthlySheetId)
            categories = summary.categories.expense if subcommand == 'expense' else summary.categories.income
            validate(transaction, categories)
            transaction[0] = str(transaction[0])[:10]
            editTransaction(lineIndex, transaction, service, subcommand, monthlySheetId, summary.title)
            return
        if command == 'summary':
            printHeader("|  Month     |  Expenses  |  Income   |", 39)
            for month in MONTH_COLS.keys():
                if len(sys.argv) > 2 and sys.argv[2] != month.lower():
                    continue
                summary = readSummaryPage(service, sheetIds[month.lower()])
                row = "|  {0:<9} |  {1:<8s}  |  {2:<8s} |"
                print(row.format(summary.title.split(" ")[0], summary.cells[14][1], summary.cells[14][7]))
                if datetime.now().strftime("%b") == month:
                    break
            return
        monthlySheetId = sheetIds[param]
        if command == 'log':
            expenses = readTransactions(service, monthlySheetId, "expense")
            income = readTransactions(service, monthlySheetId, "income")
            logTransactions(expenses, "{0} Expense Log".format(param.capitalize()))
            logTransactions(income, "{0} Income Log".format(param.capitalize()))
            return
        summary = readSummaryPage(service, monthlySheetId)
        if command == 'categories':
            listCategories(summary.categories.expense, "{0} Expenses by Category".format(param.capitalize()))
            listCategories(summary.categories.income, "{0} Income by Category".format(param.capitalize()))
        elif command == 'sync':
            sync(service, sheetIds[ANNUAL_ID_KEY], 'Expenses', summary.title, summary.categories.expense)
            sync(service, sheetIds[ANNUAL_ID_KEY], 'Income', summary.title, summary.categories.income)
    except UserWarning as e:
        print(str(e), file=sys.stderr)
        
if __name__ == '__main__':
    main()