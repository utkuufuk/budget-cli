# create token from credentials
python3 createtoken.py

# move script to a location in $PATH and make it executable
sudo cp budget.py /usr/bin/budget
sudo chmod +x /usr/bin/budget

# move token.json and config.json into a globally accessible location with read access
mkdir -p ~/.config/budget-cli
cp token.json ~/.config/budget-cli/token.json
cp config.json ~/.config/budget-cli/config.json
chmod +r ~/.config/budget-cli/token.json
chmod +r ~/.config/budget-cli/config.json

# make the uninstallation script executable
chmod +x uninstall.sh

echo "Successfully installed budget-cli."
