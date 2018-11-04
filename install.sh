# make the script executable
chmod +x addentry.py

# create token from credentials
python3 createtoken.py

# add project directory to PATH in both .zshrc & .bashrc
WDIR="$(cd "$(dirname "$0")"; pwd)"
LINE='export PATH=$PATH:'
ZFILE=~/.zshrc
BFILE=~/.bashrc
COMMENT='\n#delete this line if you no longer use google-budget\n'
grep -qF -- "$LINE$WDIR" "$ZFILE" || echo "$COMMENT$LINE$WDIR" >> "$ZFILE"
grep -qF -- "$LINE$WDIR" "$BFILE" || echo "$COMMENT$LINE$WDIR" >> "$BFILE"
