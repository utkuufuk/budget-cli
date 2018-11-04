# google-budget
Adds transaction entries to your budget spreadsheet.

## Spreadsheet Creation
Create a *Monthly budget* spreadsheet from the [spreadsheet template gallery](https://docs.google.com/spreadsheets/u/0/?ftv=1&folder=0ACoSgW1iveL-Uk9PVA).

## Installation
 1. Complete steps 1 & 2 of the [quickstart guide](https://developers.google.com/sheets/api/quickstart/python). Make sure that you copy your `credentials.json` file into the **project root directory.**

 2. Run the installation script from the project root directory:
``` sh
chmod +x install.sh
./install.sh
```
#### Warning!!
The installation script adds the project root directory to `PATH` in both `.zshrc` and `.bashrc` so that you can use the script globally. Currently there's not an uninstallation script, so **don't forget to delete the following lines from those files:**

``` sh
#delete this line if you no longer use google-budget
export PATH=$PATH:<project_root_dir>/google-budget
```

## Usage
You can run `addexpense.py` globally in order to create a transaction entry as follows:
```
addexpense.py "<Date>,<Cost>,<Description>,<Category>"
```
For instance:
```
addexpense.py "Nov 5 2018,50,Lunch at Pizza Hut,Restaurant"
```

