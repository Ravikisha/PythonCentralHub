# Automated File Mover

import os
import shutil

# Set the source and destination directories
source = os.getcwd() + "/source/"
destination = os.getcwd() + "/destination/"

# Both directories have to exist before either is used. `os.listdir` on a
# missing path raises FileNotFoundError, and `shutil.move` into a missing one
# fails halfway through -- after some files have already moved, which is the
# worse of the two failures.
os.makedirs(source, exist_ok=True)
os.makedirs(destination, exist_ok=True)

# Give the demo something to move, so a first run shows the behaviour rather
# than an empty directory listing.
if not os.listdir(source):
    for name in ("notes.txt", "report.pdf", "photo.jpg", "archive.zip"):
        with open(os.path.join(source, name), "w", encoding="utf-8") as f:
            f.write("demo file\n")
    print(f"source was empty, so 4 sample files were written to {source}")

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
            
left = os.listdir(source)
print(f"\nMove Complete: {len(files) - len(left)} moved, "
      f"{len(left)} left behind")
if left:
    print(f"  left in place: {', '.join(sorted(left))}")
    print(f"  (the filter only moves {', '.join(file_types)})")