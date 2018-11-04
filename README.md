# google-budget
Adds transaction entries to the budget spreadsheet.

## Installation
``` sh
pip3 install --upgrade google-api-python-client oauth2client
```

## Usage
In first use run the `init.py` script in order to create the `token.json` file:
```
python3 init.py
```

With the `token.json` file in the working directory, run the `addentry.py` similar to the following example in order to create a transaction entry:
```
python3 addentry.py "Nov 5 2018,90,Pazar Alışverişi,Groceries"
```

