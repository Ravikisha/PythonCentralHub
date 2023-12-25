# Automated File Mover

import os
import shutil

# Set the source and destination directories
source = os.getcwd() + "/source/"
destination = os.getcwd() + "/destination/"

# Get the list of files in the source directory
files = os.listdir(source)

# Select File Types to Move
file_types = ["txt", "pdf", "png", "jpg", "jpeg"]

# Move the files to the destination directory
for file in files:
    for file_type in file_types:
        if file.endswith(file_type):
            shutil.move(source + file, destination + file)
            print("Moved " + file + " to " + destination + file)
            
# End of File
print("Move Complete")