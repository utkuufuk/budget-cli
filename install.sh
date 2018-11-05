# make the uninstallation script executable
chmod +x uninstall.sh

# move script to a location in PATH and make it executable
cp addexpense.py ~/.local/bin/addexpense
chmod +x ~/.local/bin/addexpense

# create token from credentials
python3 createtoken.py

# move token.json to a globally accessible location with read access (~/.local/share/)
cp token.json ~/.local/share/token.json
chmod +r ~/.local/share/token.json
