# make the uninstallation script executable
chmod +x uninstall.sh

# move script to a location in PATH and make it executable
cp budget.py ~/.local/bin/budget
chmod +x ~/.local/bin/budget

# create token from credentials
python3 createtoken.py

# move token.json to a globally accessible location with read access (~/.local/share/)
mkdir -p ~/.local/share/budget-cli
cp token.json ~/.local/share/budget-cli/token.json
chmod +r ~/.local/share/budget-cli/token.json
echo "Successfully installed budget-cli."
