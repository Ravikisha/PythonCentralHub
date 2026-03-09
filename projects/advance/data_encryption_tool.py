from cryptography.fernet import Fernet

class DataEncryptionTool:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt(self, data):
        encrypted = self.cipher.encrypt(data.encode())
        print(f"Encrypted: {encrypted}")
        return encrypted

    def decrypt(self, encrypted):
        decrypted = self.cipher.decrypt(encrypted).decode()
        print(f"Decrypted: {decrypted}")
        return decrypted

if __name__ == "__main__":
    print("Data Encryption Tool Demo")
    tool = DataEncryptionTool()
    secret = tool.encrypt("Sensitive information")
    tool.decrypt(secret)
