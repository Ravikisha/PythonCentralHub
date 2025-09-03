# File Encryption/Decryption Tool

import os
import hashlib
import secrets
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import zipfile
import shutil
from pathlib import Path
from typing import Optional, List
import json
import getpass
from datetime import datetime

class FileEncryption:
    def __init__(self):
        self.key = None
        self.fernet = None
        
    def generate_key_from_password(self, password: str, salt: bytes = None) -> tuple:
        """Generate encryption key from password using PBKDF2"""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def set_key(self, password: str, salt: bytes = None) -> bytes:
        """Set encryption key from password"""
        self.key, salt = self.generate_key_from_password(password, salt)
        self.fernet = Fernet(self.key)
        return salt
    
    def generate_random_key(self) -> bytes:
        """Generate a random encryption key"""
        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)
        return self.key
    
    def encrypt_file(self, file_path: str, output_path: str = None, 
                    preserve_original: bool = True) -> dict:
        """Encrypt a single file"""
        if not self.fernet:
            raise ValueError("No encryption key set")
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine output path
        if output_path is None:
            output_path = file_path.with_suffix(file_path.suffix + '.encrypted')
        else:
            output_path = Path(output_path)
        
        try:
            # Read and encrypt file
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            encrypted_data = self.fernet.encrypt(file_data)
            
            # Create metadata
            metadata = {
                'original_name': file_path.name,
                'original_size': len(file_data),
                'encrypted_size': len(encrypted_data),
                'timestamp': datetime.now().isoformat(),
                'checksum': hashlib.sha256(file_data).hexdigest()
            }
            
            # Write encrypted file with metadata
            with open(output_path, 'wb') as encrypted_file:
                # Write metadata as JSON header
                metadata_json = json.dumps(metadata).encode()
                metadata_size = len(metadata_json)
                
                # Write metadata size (4 bytes) + metadata + encrypted data
                encrypted_file.write(metadata_size.to_bytes(4, byteorder='big'))
                encrypted_file.write(metadata_json)
                encrypted_file.write(encrypted_data)
            
            # Remove original file if not preserving
            if not preserve_original:
                os.remove(file_path)
            
            return {
                'status': 'success',
                'original_file': str(file_path),
                'encrypted_file': str(output_path),
                'metadata': metadata
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'original_file': str(file_path)
            }
    
    def decrypt_file(self, encrypted_file_path: str, output_path: str = None,
                    preserve_encrypted: bool = True) -> dict:
        """Decrypt a single file"""
        if not self.fernet:
            raise ValueError("No encryption key set")
        
        encrypted_file_path = Path(encrypted_file_path)
        if not encrypted_file_path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {encrypted_file_path}")
        
        try:
            # Read encrypted file
            with open(encrypted_file_path, 'rb') as encrypted_file:
                # Read metadata size
                metadata_size_bytes = encrypted_file.read(4)
                if len(metadata_size_bytes) != 4:
                    raise ValueError("Invalid encrypted file format")
                
                metadata_size = int.from_bytes(metadata_size_bytes, byteorder='big')
                
                # Read metadata
                metadata_json = encrypted_file.read(metadata_size)
                metadata = json.loads(metadata_json.decode())
                
                # Read encrypted data
                encrypted_data = encrypted_file.read()
            
            # Decrypt data
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            # Verify checksum
            if hashlib.sha256(decrypted_data).hexdigest() != metadata['checksum']:
                raise ValueError("File integrity check failed - data may be corrupted")
            
            # Determine output path
            if output_path is None:
                output_path = encrypted_file_path.parent / metadata['original_name']
            else:
                output_path = Path(output_path)
            
            # Write decrypted file
            with open(output_path, 'wb') as decrypted_file:
                decrypted_file.write(decrypted_data)
            
            # Remove encrypted file if not preserving
            if not preserve_encrypted:
                os.remove(encrypted_file_path)
            
            return {
                'status': 'success',
                'encrypted_file': str(encrypted_file_path),
                'decrypted_file': str(output_path),
                'metadata': metadata
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'encrypted_file': str(encrypted_file_path)
            }
    
    def encrypt_directory(self, directory_path: str, output_path: str = None,
                         include_subdirs: bool = True) -> dict:
        """Encrypt all files in a directory"""
        directory_path = Path(directory_path)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if output_path is None:
            output_path = directory_path.with_suffix('.encrypted_archive')
        else:
            output_path = Path(output_path)
        
        results = []
        temp_dir = Path("temp_encryption")
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Get all files to encrypt
            if include_subdirs:
                files = list(directory_path.rglob('*'))
            else:
                files = list(directory_path.glob('*'))
            
            files = [f for f in files if f.is_file()]
            
            # Encrypt each file
            for file_path in files:
                relative_path = file_path.relative_to(directory_path)
                temp_encrypted_path = temp_dir / (str(relative_path) + '.encrypted')
                temp_encrypted_path.parent.mkdir(parents=True, exist_ok=True)
                
                result = self.encrypt_file(str(file_path), str(temp_encrypted_path))
                results.append(result)
            
            # Create archive of encrypted files
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(temp_dir)
                        zipf.write(file_path, arcname)
            
            # Clean up temp directory
            shutil.rmtree(temp_dir)
            
            successful_encryptions = sum(1 for r in results if r['status'] == 'success')
            
            return {
                'status': 'success',
                'directory': str(directory_path),
                'archive': str(output_path),
                'total_files': len(results),
                'successful': successful_encryptions,
                'failed': len(results) - successful_encryptions,
                'results': results
            }
            
        except Exception as e:
            # Clean up on error
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            
            return {
                'status': 'error',
                'error': str(e),
                'directory': str(directory_path)
            }
    
    def decrypt_directory(self, archive_path: str, output_directory: str = None) -> dict:
        """Decrypt an encrypted directory archive"""
        archive_path = Path(archive_path)
        if not archive_path.exists():
            raise FileNotFoundError(f"Archive not found: {archive_path}")
        
        if output_directory is None:
            output_directory = archive_path.with_suffix('')
        else:
            output_directory = Path(output_directory)
        
        output_directory.mkdir(exist_ok=True)
        temp_dir = Path("temp_decryption")
        
        try:
            # Extract archive
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            results = []
            
            # Decrypt each file
            for encrypted_file in temp_dir.rglob('*.encrypted'):
                relative_path = encrypted_file.relative_to(temp_dir)
                relative_path = Path(str(relative_path).replace('.encrypted', ''))
                
                output_file_path = output_directory / relative_path
                output_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                result = self.decrypt_file(str(encrypted_file), str(output_file_path))
                results.append(result)
            
            # Clean up temp directory
            shutil.rmtree(temp_dir)
            
            successful_decryptions = sum(1 for r in results if r['status'] == 'success')
            
            return {
                'status': 'success',
                'archive': str(archive_path),
                'output_directory': str(output_directory),
                'total_files': len(results),
                'successful': successful_decryptions,
                'failed': len(results) - successful_decryptions,
                'results': results
            }
            
        except Exception as e:
            # Clean up on error
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            
            return {
                'status': 'error',
                'error': str(e),
                'archive': str(archive_path)
            }
    
    def save_key_to_file(self, key_file_path: str, password: str = None):
        """Save encryption key to file (optionally password protected)"""
        if not self.key:
            raise ValueError("No key to save")
        
        key_data = {
            'key': base64.b64encode(self.key).decode(),
            'timestamp': datetime.now().isoformat()
        }
        
        if password:
            # Encrypt the key data with password
            temp_encryption = FileEncryption()
            salt = temp_encryption.set_key(password)
            
            key_json = json.dumps(key_data).encode()
            encrypted_key = temp_encryption.fernet.encrypt(key_json)
            
            protected_data = {
                'encrypted': True,
                'salt': base64.b64encode(salt).decode(),
                'data': base64.b64encode(encrypted_key).decode()
            }
            
            with open(key_file_path, 'w') as f:
                json.dump(protected_data, f, indent=2)
        else:
            key_data['encrypted'] = False
            with open(key_file_path, 'w') as f:
                json.dump(key_data, f, indent=2)
    
    def load_key_from_file(self, key_file_path: str, password: str = None):
        """Load encryption key from file"""
        with open(key_file_path, 'r') as f:
            key_data = json.load(f)
        
        if key_data.get('encrypted', False):
            if not password:
                raise ValueError("Password required for encrypted key file")
            
            # Decrypt the key data
            salt = base64.b64decode(key_data['salt'])
            encrypted_data = base64.b64decode(key_data['data'])
            
            temp_encryption = FileEncryption()
            temp_encryption.set_key(password, salt)
            
            decrypted_json = temp_encryption.fernet.decrypt(encrypted_data)
            actual_key_data = json.loads(decrypted_json.decode())
            
            self.key = base64.b64decode(actual_key_data['key'])
        else:
            self.key = base64.b64decode(key_data['key'])
        
        self.fernet = Fernet(self.key)

def create_sample_files():
    """Create sample files for testing"""
    sample_dir = Path("sample_files")
    sample_dir.mkdir(exist_ok=True)
    
    # Create text file
    with open(sample_dir / "sample.txt", 'w') as f:
        f.write("This is a sample text file for encryption testing.\n")
        f.write("It contains multiple lines of text.\n")
        f.write("The content will be encrypted and then decrypted.\n")
    
    # Create JSON file
    sample_data = {
        "name": "John Doe",
        "age": 30,
        "city": "New York",
        "hobbies": ["reading", "coding", "traveling"]
    }
    
    with open(sample_dir / "data.json", 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    # Create binary file
    with open(sample_dir / "binary_data.bin", 'wb') as f:
        f.write(os.urandom(1024))  # 1KB of random data
    
    # Create subdirectory with files
    sub_dir = sample_dir / "subdirectory"
    sub_dir.mkdir(exist_ok=True)
    
    with open(sub_dir / "nested_file.txt", 'w') as f:
        f.write("This is a file in a subdirectory.")
    
    print(f"Sample files created in {sample_dir}")

def main():
    """Main function to run the file encryption tool"""
    encryption = FileEncryption()
    
    while True:
        print("\n=== File Encryption/Decryption Tool ===")
        print("1. Set password for encryption")
        print("2. Generate random key")
        print("3. Encrypt single file")
        print("4. Decrypt single file")
        print("5. Encrypt directory")
        print("6. Decrypt directory archive")
        print("7. Save key to file")
        print("8. Load key from file")
        print("9. Create sample files for testing")
        print("10. View current key status")
        print("0. Exit")
        
        try:
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                password = getpass.getpass("Enter password for encryption: ")
                if len(password) < 8:
                    print("Warning: Password should be at least 8 characters long")
                
                salt = encryption.set_key(password)
                print("✓ Encryption key generated from password")
                print(f"Salt: {base64.b64encode(salt).decode()}")
            
            elif choice == '2':
                key = encryption.generate_random_key()
                print("✓ Random encryption key generated")
                print(f"Key: {base64.b64encode(key).decode()}")
                print("⚠ Make sure to save this key - you'll need it for decryption!")
            
            elif choice == '3':
                if not encryption.fernet:
                    print("❌ Please set an encryption key first (option 1 or 2)")
                    continue
                
                file_path = input("Enter file path to encrypt: ").strip()
                preserve = input("Preserve original file? (y/n): ").strip().lower() == 'y'
                
                result = encryption.encrypt_file(file_path, preserve_original=preserve)
                
                if result['status'] == 'success':
                    print("✓ File encrypted successfully!")
                    print(f"Original: {result['original_file']}")
                    print(f"Encrypted: {result['encrypted_file']}")
                    print(f"Original size: {result['metadata']['original_size']} bytes")
                    print(f"Encrypted size: {result['metadata']['encrypted_size']} bytes")
                else:
                    print(f"❌ Encryption failed: {result['error']}")
            
            elif choice == '4':
                if not encryption.fernet:
                    print("❌ Please set an encryption key first (option 1 or 2)")
                    continue
                
                file_path = input("Enter encrypted file path: ").strip()
                preserve = input("Preserve encrypted file? (y/n): ").strip().lower() == 'y'
                
                result = encryption.decrypt_file(file_path, preserve_encrypted=preserve)
                
                if result['status'] == 'success':
                    print("✓ File decrypted successfully!")
                    print(f"Encrypted: {result['encrypted_file']}")
                    print(f"Decrypted: {result['decrypted_file']}")
                    print(f"Original name: {result['metadata']['original_name']}")
                    print(f"Checksum verified: ✓")
                else:
                    print(f"❌ Decryption failed: {result['error']}")
            
            elif choice == '5':
                if not encryption.fernet:
                    print("❌ Please set an encryption key first (option 1 or 2)")
                    continue
                
                dir_path = input("Enter directory path to encrypt: ").strip()
                include_subdirs = input("Include subdirectories? (y/n): ").strip().lower() == 'y'
                
                print("Encrypting directory... This may take a while for large directories.")
                result = encryption.encrypt_directory(dir_path, include_subdirs=include_subdirs)
                
                if result['status'] == 'success':
                    print("✓ Directory encrypted successfully!")
                    print(f"Directory: {result['directory']}")
                    print(f"Archive: {result['archive']}")
                    print(f"Total files: {result['total_files']}")
                    print(f"Successful: {result['successful']}")
                    print(f"Failed: {result['failed']}")
                else:
                    print(f"❌ Directory encryption failed: {result['error']}")
            
            elif choice == '6':
                if not encryption.fernet:
                    print("❌ Please set an encryption key first (option 1 or 2)")
                    continue
                
                archive_path = input("Enter encrypted archive path: ").strip()
                output_dir = input("Enter output directory (or press Enter for default): ").strip()
                
                if not output_dir:
                    output_dir = None
                
                print("Decrypting archive... This may take a while for large archives.")
                result = encryption.decrypt_directory(archive_path, output_dir)
                
                if result['status'] == 'success':
                    print("✓ Archive decrypted successfully!")
                    print(f"Archive: {result['archive']}")
                    print(f"Output directory: {result['output_directory']}")
                    print(f"Total files: {result['total_files']}")
                    print(f"Successful: {result['successful']}")
                    print(f"Failed: {result['failed']}")
                else:
                    print(f"❌ Archive decryption failed: {result['error']}")
            
            elif choice == '7':
                if not encryption.key:
                    print("❌ No encryption key to save")
                    continue
                
                key_file = input("Enter key file path: ").strip()
                protect = input("Protect key with password? (y/n): ").strip().lower() == 'y'
                
                if protect:
                    password = getpass.getpass("Enter password to protect key: ")
                    encryption.save_key_to_file(key_file, password)
                else:
                    encryption.save_key_to_file(key_file)
                
                print("✓ Key saved successfully!")
            
            elif choice == '8':
                key_file = input("Enter key file path: ").strip()
                
                try:
                    # Check if file is encrypted
                    with open(key_file, 'r') as f:
                        key_data = json.load(f)
                    
                    if key_data.get('encrypted', False):
                        password = getpass.getpass("Enter password for key file: ")
                        encryption.load_key_from_file(key_file, password)
                    else:
                        encryption.load_key_from_file(key_file)
                    
                    print("✓ Key loaded successfully!")
                    
                except Exception as e:
                    print(f"❌ Failed to load key: {e}")
            
            elif choice == '9':
                create_sample_files()
            
            elif choice == '10':
                if encryption.key:
                    print("✓ Encryption key is set")
                    print(f"Key: {base64.b64encode(encryption.key).decode()[:32]}...")
                else:
                    print("❌ No encryption key set")
            
            elif choice == '0':
                print("Thank you for using the File Encryption Tool!")
                break
            
            else:
                print("Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
