import os
import shutil

class CloudStorageManager:
    def __init__(self, storage_dir):
        self.storage_dir = storage_dir
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

    def upload_file(self, file_path):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        dest = os.path.join(self.storage_dir, os.path.basename(file_path))
        shutil.copy(file_path, dest)
        print(f"Uploaded {file_path} to cloud storage.")

    def list_files(self):
        files = os.listdir(self.storage_dir)
        print("Files in cloud storage:", files)
        return files

    def download_file(self, file_name, dest_dir):
        src = os.path.join(self.storage_dir, file_name)
        if not os.path.isfile(src):
            raise FileNotFoundError(f"File not found in cloud storage: {file_name}")
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        dest = os.path.join(dest_dir, file_name)
        shutil.copy(src, dest)
        print(f"Downloaded {file_name} to {dest_dir}.")

if __name__ == "__main__":
    print("Cloud Storage Manager Demo")
    manager = CloudStorageManager("cloud_storage")
    # Demo: upload, list, download
    # manager.upload_file("example.txt")
    manager.list_files()
    # manager.download_file("example.txt", "downloads")
