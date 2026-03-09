"""
Basic Chatroom App

A Python application that allows multiple users to communicate in a chatroom.
Features include:
- Server-side implementation to manage multiple clients.
- Client-side implementation for sending and receiving messages.
"""

import socket
import threading

# Server-side implementation
class ChatServer:
    def __init__(self, host="localhost", port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        print(f"Server started on {host}:{port}")

        self.clients = []

    def broadcast(self, message, client_socket):
        """Send a message to all connected clients except the sender."""
        for client in self.clients:
            if client != client_socket:
                try:
                    client.send(message)
                except:
                    self.clients.remove(client)

    def handle_client(self, client_socket):
        """Handle communication with a connected client."""
        while True:
            try:
                message = client_socket.recv(1024)
                if message:
                    print(f"Received: {message.decode('utf-8')}")
                    self.broadcast(message, client_socket)
            except:
                self.clients.remove(client_socket)
                client_socket.close()
                break

    def run(self):
        """Start the server and accept incoming connections."""
        while True:
            client_socket, client_address = self.server.accept()
            print(f"New connection: {client_address}")
            self.clients.append(client_socket)

            threading.Thread(target=self.handle_client, args=(client_socket,)).start()


# Client-side implementation
class ChatClient:
    def __init__(self, host="localhost", port=12345):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

        threading.Thread(target=self.receive_messages).start()

    def send_message(self, message):
        """Send a message to the server."""
        self.client.send(message.encode("utf-8"))

    def receive_messages(self):
        """Receive messages from the server."""
        while True:
            try:
                message = self.client.recv(1024).decode("utf-8")
                print(message)
            except:
                print("Disconnected from server.")
                self.client.close()
                break


if __name__ == "__main__":
    choice = input("Do you want to start the server or client? (server/client): ").strip().lower()

    if choice == "server":
        server = ChatServer()
        server.run()
    elif choice == "client":
        client = ChatClient()
        print("Type your messages below:")
        while True:
            msg = input()
            client.send_message(msg)
    else:
        print("Invalid choice. Exiting.")
