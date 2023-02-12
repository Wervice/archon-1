import os
import sys
from libs import dashboard as dashboard
import shutil
import re
from termcolor import colored
from datetime import datetime
now = datetime.now()
# Date and time as a formatted string
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
def is_unc_path(path):
    unc_path = re.compile(r"^\\\\[\w\.]+\\.+")
    return bool(unc_path.match(path))
try:
    if len(sys.argv) == 1:
        # Writes the breefing
        print(open(".\\assets\\breefing.txt", "r").read())
    else:
        if sys.argv[1] == "backup":
            # Backup a single file
            try:
                # Copies the file to the destination location
                open(sys.argv[3], "wb").write(open(sys.argv[2], "rb").read())
                # Shows the copy indicator
                print(colored("[-] Copy: " + sys.argv[2] + " => " + sys.argv[3], "blue"))
                # Check the copy
                if (open(sys.argv[2], "rb").read() == open(sys.argv[3], "rb").read()):
                    print(colored("[*] Backup file", "green"))
                    # Push to the dashboard
                    dashboard.push("success", sys.argv[2], sys.argv[3])
                    dashboard.show()
                else:
                    # Push to the dashboard if copy failed
                    dashboard.push("fail_copyisfalse",
                                   sys.argv[2], sys.argv[3])
                    dashboard.show()
                    # Print error message
                    print("The backup is not the same as the orginal.")
            except FileNotFoundError:
                dashboard.push("fail_filenotfound", sys.argv[2], sys.argv[3])
                dashboard.show()
                print(colored("File Not Found", "red"))
        elif sys.argv[1] == "fbackup":
            # Backup a folder and compress it as xztar file.
            try:
                if is_unc_path(sys.argv[3]):
                    print(colored("[-] Backup folder to network location", "blue"))
                else:
                    print(colored("[-] Backup folder to local path", "blue"))
                foldername = os.path.dirname(sys.argv[2]).split(
                    "\\")[len(os.path.dirname(sys.argv[2]).split("\\"))-1]  # Get foldername
                print(colored("[-] Make compressed tar archive", "blue"))  # Print "Make the archive"
                # Write the metadata to the backupfolder
                open(sys.argv[2]+"archon_metadata",
                     "w").write(dt_string+";\n"+str(now)+";\n"+os.getlogin())
                # Make the arcive
                shutil.make_archive(
                    sys.argv[3]+"\\"+foldername, 'xztar', sys.argv[2])
                # Delete the metadata from the folder
                os.remove(sys.argv[2]+"archon_metadata")
                print(colored("[*] Backup folder", "green"))  # Print Done
                # Push to the dashboard
                dashboard.push("success", sys.argv[2], sys.argv[3], True)
                dashboard.show()
            except FileNotFoundError:
                dashboard.push("fail_filenotfound",
                               sys.argv[2], sys.argv[3], True)
                dashboard.show()
                print(colored("File Not Found\nExiting now", "red"))
        elif sys.argv[1] == "restore":
            try:
                print(colored("[-] Getting backups", "blue"))  # Status message
                # Download the backup
                shutil.copy(sys.argv[2], ".\\temp_archon_restore_file.tmp")
                if os.path.exists(".\\temp_archon_restore_file.tmp"):
                    print(colored("[*] Got backups", "green"))
                else:
                    print(colored("[x] Getting backups failed. Please try again.", "red"))
                    print("Exiting now")
                    exit()
                print(colored("[-] Restoring files", "blue"))  # Status message
                # Unpack the downloaded archive
                shutil.unpack_archive(
                    ".\\temp_archon_restore_file.tmp", sys.argv[3], format="xztar")
                print(colored("[*] Restoring files", "green"))
                # Read the metadata to the chache
                metadata = open(sys.argv[3]+"archon_metadata", "r").read()
                print(colored("[-] Remove temporary files", "blue"))  # Status message
                os.remove(sys.argv[3]+"archon_metadata")  # Remove metadata file
                os.remove(".\\temp_archon_restore_file.tmp") # Remove downloaded file
                # Print status message and metadata time
                print(colored("[*] Restored from backup (Backup Time " +
                    metadata.split(";\n")[0]+")", "green"))
            except FileNotFoundError:
                print(colored("File Not Found\nExiting now", "red"))

except IndexError:
    print(colored("You need more arguments.\nExiting now", "red"))