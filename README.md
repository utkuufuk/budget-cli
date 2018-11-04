# google-budget
Adds transaction entries to your budget spreadsheet.

## Installation
Install dependencies:
``` sh
pip3 install --upgrade google-api-python-client oauth2client
```

Run the installation script from the project root directory:
``` sh
chmod +x install.sh
./install.sh
```

## Usage
You can run `addexpense.py` globally in order to create a transaction entry:
```
addexpense.py "Nov 5 2018,90,Pazar Alışverişi,Groceries"
```

