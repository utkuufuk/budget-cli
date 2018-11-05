# google-budget
Add expense entries to your Google budget spreadsheet from the CLI.

## Preliminaries
 1. Create a *monthly budget* spreadsheet from the [spreadsheet template gallery](https://docs.google.com/spreadsheets/u/0/?ftv=1&folder=0ACoSgW1iveL-Uk9PVA) if you don't already have one.

 2. Take note of your spreadsheet ID in the page URL when the new sheet opens up.

``` cmd
https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit#gid=<SHEET_ID>
```

 3. Replace the default ID with your **spreadsheet ID** in the `addexpense.py` file:
``` python
# replace this with your spreadsheet ID
SPREADSHEET_ID = '1jANO8_sbQ5pLEAJbyxWcQiklPboPtSp8ijrp_RTD0Aw'
```

## Installation
 1. Complete steps 1 & 2 of the [quickstart guide](https://developers.google.com/sheets/api/quickstart/python). Make sure that you copy your `credentials.json` file into the **project root directory.**

 2. Run the installation script from the project root directory:
``` sh
chmod +x install.sh
./install.sh
```

## Uninstallation
Run the uninstallation script from the project root directory:
``` sh
./uninstall.sh
```

## Usage
You can run `addexpense` globally in order to create a transaction entry as follows:
```
addexpense "<Date>,<Amount>,<Description>,<Category>"
```
For instance:
```
addexpense "Nov 5 2018,90,Lunch at Pizza Hut,Restaurant"
```

![Example](example.png)
