# budget-cli
 * insert/edit transaction entries
 * view transaction logs & summary
 * synchronize with annual budget
 * only configure once in a year

![Demo](demo.gif)

## Preliminaries
 1. Create *monthly budget* spreadsheets for each month from the [spreadsheet template gallery](https://docs.google.com/spreadsheets/u/0/?ftv=1&folder=0ACoSgW1iveL-Uk9PVA).

 2. Optionally, create an additional *annual budget* spreadsheet if you want to use the synchronization feature.

 3. Take note of the SPREADSHEET_IDs which is embedded inside the URL:
``` cmd
https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit#gid=<SHEET_ID>
```

## Install
 1. Complete steps 1 in the [quickstart guide](https://developers.google.com/sheets/api/quickstart/python). Make sure that you copy the **`credentials.json`** file into **project directory.**

 2. Update spreadsheet IDs inside [config.json](config.json) with your own monthly budget spreadsheet IDs.

 3. From project directory:
``` sh
./install.sh
```
 
## Uninstall
``` sh
./uninstall.sh
```

## Usage
 * For `summary`, `categories`, `log` and `sync` commands, this month's spreadsheet will be used unless specified explicitly.

 * For `expense` and `income` commands, today's date will be assumed and this month's spreadsheet will be used unless date is specified explicitly.

 * For `edit` command, the transaction date will stay the same and this month's spreadsheet will be used unless date is specified explicitly, in which case the month will be determined accordingly.

### Transaction Entry
``` sh
# insert expense transaction in June budget
budget expense "Jun 29, 40, Pizza, Food"

# insert expense transaction for today in this month's budget
budget expense "40, Pizza, Food"

# insert income transaction in August budget
budget income "Aug 2, 3000, Salary, Paycheck"

# insert income transaction for today in this month's budget
budget income "3000, Salary, Paycheck"

# edit 4th income transaction in this month's budget (see `budget log` for transaction number)
budget edit income 4 "65, Tax Return, Other"

# edit 5th expense transaction in September budget (see `budget log sep` for transaction number)
budget edit expense 5 "Sep 17, Mobile Plan, Communication"

# execute all transaction commands within ./example.txt (path can be relative or absolute)
budget insert ./example.txt
```

Here's what an input file might look like when using the `insert` command:
```txt
expense "Jun 29, 40, Pizza, Food"
expense "40, Pizza, Food"
income "Aug 2, 3000, Salary, Paycheck"
income "3000, Salary, Paycheck"
```


### Summary
``` sh
# print monthly budget summary for all months so far
budget summary

# print monthly budget summary for January
budget summary jan
```

### Categories
``` sh
# list all monthly budget categories & amounts for this month
budget categories

# list all monthly budget categories & amounts for February
budget categories feb
```

### Log
``` sh
# log monthly budget transaction history for this month
budget log

# log monthly budget transaction history for March
budget log mar
```

### Annual Budget Synchronization
In order to synchronize with annual budget, expense & income categories must be exactly the same across all monthly budget spreadsheets and the annual budget spreadsheet.

``` sh
# update annual budget with expenses & income of this month
budget sync

# update annual budget with expenses & income of April
budget sync apr
```
