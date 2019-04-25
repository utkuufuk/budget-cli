set -e

pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib oauth2client

# create token from credentials
python3 createtoken.py

# move token.json and config.json into a globally accessible location with read access
mkdir -p ~/.budget-cli
cp token.json ~/.budget-cli/token.json
cp config.json ~/.budget-cli/config.json
chmod +r ~/.budget-cli/token.json
chmod +r ~/.budget-cli/config.json

# run setup.py
pip3 install .
