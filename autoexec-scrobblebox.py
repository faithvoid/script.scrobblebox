import xbmc
import xbmcgui
import os

autoexec_path = 'Q:\\scripts\\autoexec.py'
line_to_add_or_remove = "xbmc.executebuiltin('XBMC.RunScript(Q:\\\\scripts\\\\ScrobbleBox\\\\scrobblebox.py)')"

# Function to add the line to autoexec.py
def add_line():
    # Check if autoexec.py exists
    if os.path.exists(autoexec_path):
        with open(autoexec_path, 'r') as file:
            content = file.readlines()

        # Clean up the content to remove extra newlines or spaces
        content = [line.rstrip() for line in content]

        # Check if the line is already in autoexec.py (accounting for potential newline characters)
        if line_to_add_or_remove not in content:
            # Add the line at the end
            with open(autoexec_path, 'a') as file:
                file.write('\n' + line_to_add_or_remove)
            xbmcgui.Dialog().ok("Success!", "ScrobbleBox is now enabled on startup!")
        else:
            xbmcgui.Dialog().ok("No Changes", "ScrobbleBox is already enabled on startup!")
    else:
        # If autoexec.py does not exist, create it and add the line
        with open(autoexec_path, 'w') as file:
            file.write(line_to_add_or_remove + '\n')
        xbmcgui.Dialog().ok("Autoexec Created", "ScrobbleBox is now enabled on startup!")

# Function to remove the line from autoexec.py
def remove_line():
    # Check if autoexec.py exists
    if os.path.exists(autoexec_path):
        with open(autoexec_path, 'r') as file:
            content = file.readlines()

        # Clean up the content to remove extra newlines or spaces
        content = [line.rstrip() for line in content]

        # Check if the line exists in autoexec.py
        if line_to_add_or_remove in content:
            # Remove the line
            content.remove(line_to_add_or_remove)
            with open(autoexec_path, 'w') as file:
                file.write('\n'.join(content) + '\n')
            xbmcgui.Dialog().ok("Success!", "Scrobblebox disabled on startup!")
        else:
            xbmcgui.Dialog().ok("No Changes", "Scrobblebox already disabled on startup!")
    else:
        xbmcgui.Dialog().ok("Autoexec Not Found", "autoexec.py does not exist!")

# Function to show the choice dialog using XBMC GUI
def show_dialog():
    # Create a dialog to ask the user what action to take
    dialog = xbmcgui.Dialog()
    result = dialog.select("ScrobbleBox - Startup", ["Enable ScrobbleBox On Startup", "Disable ScrobbleBox On Startup"])

    if result == 0:  # "Add line" option
        add_line()
    elif result == 1:  # "Remove line" option
        remove_line()
    else:
        xbmcgui.Dialog().ok("No Selection!", "No action selected or dialog closed!")

# Run the GUI dialog
show_dialog()
