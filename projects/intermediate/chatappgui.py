#!/usr/bin/env python3
"""
Chat Application with GUI (Tkinter)
A comprehensive chat application with client-server architecture using Tkinter for GUI.

Features:
- Client-server socket communication
- Multi-user chat rooms
- Private messaging
- User authentication
- File sharing capabilities
- Emoji support
- Chat history

Requirements:
- tkinter (built-in)
- socket (built-in)
- threading (built-in)
- json (built-in)

Author: Python Central Hub
Date: 2025-09-06
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import socket
import threading
import json
import datetime
import base64
import os
from pathlib import Path


class ChatServer:
    """Chat server to handle multiple client connections."""
    
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.clients = {}
        self.rooms = {'general': []}
        self.server_socket = None
        self.running = False
        
    def start_server(self):
        """Start the chat server."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"🚀 Chat server started on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"📱 New connection from {address}")
                    
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error:
                    if self.running:
                        print("❌ Server socket error")
                    break
                    
        except Exception as e:
            print(f"❌ Server error: {e}")
        finally:
            self.stop_server()
    
    def handle_client(self, client_socket, address):
        """Handle individual client connections."""
        username = None
        try:
            while self.running:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                try:
                    message = json.loads(data)
                    response = self.process_message(message, client_socket, address)
                    
                    if message['type'] == 'join':
                        username = message['username']
                        self.clients[username] = {
                            'socket': client_socket,
                            'address': address,
                            'room': 'general'
                        }
                        if username not in self.rooms['general']:
                            self.rooms['general'].append(username)
                    
                except json.JSONDecodeError:
                    pass
                    
        except ConnectionResetError:
            pass
        except Exception as e:
            print(f"❌ Client handler error: {e}")
        finally:
            if username and username in self.clients:
                self.remove_client(username)
            client_socket.close()
    
    def process_message(self, message, client_socket, address):
        """Process incoming messages from clients."""
        msg_type = message.get('type')
        
        if msg_type == 'join':
            self.handle_join(message, client_socket)
        elif msg_type == 'message':
            self.handle_message(message)
        elif msg_type == 'private':
            self.handle_private_message(message)
        elif msg_type == 'file':
            self.handle_file_share(message)
        elif msg_type == 'room_change':
            self.handle_room_change(message)
        elif msg_type == 'user_list':
            self.send_user_list(message['username'])
    
    def handle_join(self, message, client_socket):
        """Handle user joining the chat."""
        username = message['username']
        join_msg = {
            'type': 'system',
            'message': f"{username} joined the chat",
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.broadcast_to_room('general', join_msg)
        
        # Send welcome message to the new user
        welcome_msg = {
            'type': 'system',
            'message': f"Welcome to the chat, {username}!",
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.send_to_client(username, welcome_msg)
    
    def handle_message(self, message):
        """Handle regular chat messages."""
        room = message.get('room', 'general')
        chat_msg = {
            'type': 'message',
            'username': message['username'],
            'message': message['message'],
            'room': room,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.broadcast_to_room(room, chat_msg)
    
    def handle_private_message(self, message):
        """Handle private messages between users."""
        private_msg = {
            'type': 'private',
            'from': message['from'],
            'message': message['message'],
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.send_to_client(message['to'], private_msg)
    
    def handle_file_share(self, message):
        """Handle file sharing between users."""
        file_msg = {
            'type': 'file',
            'username': message['username'],
            'filename': message['filename'],
            'filedata': message['filedata'],
            'room': message.get('room', 'general'),
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.broadcast_to_room(message.get('room', 'general'), file_msg)
    
    def handle_room_change(self, message):
        """Handle user changing rooms."""
        username = message['username']
        old_room = message['old_room']
        new_room = message['new_room']
        
        # Remove from old room
        if old_room in self.rooms and username in self.rooms[old_room]:
            self.rooms[old_room].remove(username)
        
        # Add to new room
        if new_room not in self.rooms:
            self.rooms[new_room] = []
        if username not in self.rooms[new_room]:
            self.rooms[new_room].append(username)
        
        # Update client info
        if username in self.clients:
            self.clients[username]['room'] = new_room
    
    def send_user_list(self, username):
        """Send list of online users to a client."""
        user_list = list(self.clients.keys())
        user_msg = {
            'type': 'user_list',
            'users': user_list,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.send_to_client(username, user_msg)
    
    def broadcast_to_room(self, room, message):
        """Broadcast message to all users in a room."""
        if room not in self.rooms:
            return
        
        for username in self.rooms[room]:
            self.send_to_client(username, message)
    
    def send_to_client(self, username, message):
        """Send message to a specific client."""
        if username in self.clients:
            try:
                client_socket = self.clients[username]['socket']
                data = json.dumps(message).encode('utf-8')
                client_socket.send(data)
            except Exception as e:
                print(f"❌ Error sending to {username}: {e}")
                self.remove_client(username)
    
    def remove_client(self, username):
        """Remove client from server."""
        if username in self.clients:
            room = self.clients[username]['room']
            
            # Remove from room
            if room in self.rooms and username in self.rooms[room]:
                self.rooms[room].remove(username)
            
            # Remove from clients
            del self.clients[username]
            
            # Broadcast leave message
            leave_msg = {
                'type': 'system',
                'message': f"{username} left the chat",
                'timestamp': datetime.datetime.now().isoformat()
            }
            self.broadcast_to_room(room, leave_msg)
    
    def stop_server(self):
        """Stop the chat server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("🛑 Chat server stopped")


class ChatClient:
    """Chat client with Tkinter GUI."""
    
    def __init__(self):
        self.socket = None
        self.username = None
        self.current_room = 'general'
        self.connected = False
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the chat client GUI."""
        self.root = tk.Tk()
        self.root.title("Chat Application")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create main menu
        self.create_menu()
        
        # Connection frame
        self.create_connection_frame()
        
        # Chat frame (initially hidden)
        self.create_chat_frame()
        
        # Initially show connection frame
        self.connection_frame.pack(fill=tk.BOTH, expand=True)
    
    def create_menu(self):
        """Create application menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Share File", command=self.share_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Chat menu
        chat_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Chat", menu=chat_menu)
        chat_menu.add_command(label="Private Message", command=self.private_message)
        chat_menu.add_command(label="Change Room", command=self.change_room)
        chat_menu.add_command(label="User List", command=self.request_user_list)
    
    def create_connection_frame(self):
        """Create connection setup frame."""
        self.connection_frame = ttk.Frame(self.root)
        
        # Title
        title_label = ttk.Label(
            self.connection_frame, 
            text="💬 Chat Application", 
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=20)
        
        # Connection form
        form_frame = ttk.LabelFrame(self.connection_frame, text="Connection Settings")
        form_frame.pack(padx=50, pady=20, fill=tk.X)
        
        # Server address
        ttk.Label(form_frame, text="Server Address:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.server_entry = ttk.Entry(form_frame, width=30)
        self.server_entry.insert(0, "localhost")
        self.server_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Port
        ttk.Label(form_frame, text="Port:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.port_entry = ttk.Entry(form_frame, width=30)
        self.port_entry.insert(0, "12345")
        self.port_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Username
        ttk.Label(form_frame, text="Username:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.connection_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame, text="Connect", 
            command=self.connect_to_server
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            button_frame, text="Start Server", 
            command=self.start_local_server
        ).pack(side=tk.LEFT, padx=10)
    
    def create_chat_frame(self):
        """Create main chat interface frame."""
        self.chat_frame = ttk.Frame(self.root)
        
        # Top frame for room info
        top_frame = ttk.Frame(self.chat_frame)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.room_label = ttk.Label(top_frame, text="Room: general", font=("Arial", 12, "bold"))
        self.room_label.pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(top_frame, text="Connected", foreground="green")
        self.status_label.pack(side=tk.RIGHT)
        
        # Main chat area
        main_frame = ttk.Frame(self.chat_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Chat display
        chat_frame = ttk.LabelFrame(main_frame, text="Chat")
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            wrap=tk.WORD, 
            state=tk.DISABLED,
            height=20
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Users list
        users_frame = ttk.LabelFrame(main_frame, text="Online Users")
        users_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        self.users_listbox = tk.Listbox(users_frame, width=20)
        self.users_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.users_listbox.bind('<Double-1>', self.on_user_double_click)
        
        # Message input
        input_frame = ttk.Frame(self.chat_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.message_entry = ttk.Entry(input_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_entry.bind('<Return>', self.send_message)
        
        ttk.Button(
            input_frame, text="Send", 
            command=self.send_message
        ).pack(side=tk.RIGHT)
        
        # Emoji frame
        emoji_frame = ttk.Frame(self.chat_frame)
        emoji_frame.pack(fill=tk.X, padx=5, pady=5)
        
        emojis = ['😀', '😂', '😍', '👍', '👎', '❤️', '😢', '😮', '😡', '🤔']
        for emoji in emojis:
            ttk.Button(
                emoji_frame, text=emoji, width=3,
                command=lambda e=emoji: self.insert_emoji(e)
            ).pack(side=tk.LEFT, padx=2)
    
    def connect_to_server(self):
        """Connect to chat server."""
        try:
            server = self.server_entry.get().strip()
            port = int(self.port_entry.get().strip())
            username = self.username_entry.get().strip()
            
            if not username:
                messagebox.showerror("Error", "Please enter a username")
                return
            
            # Create socket connection
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((server, port))
            
            self.username = username
            self.connected = True
            
            # Send join message
            join_msg = {
                'type': 'join',
                'username': username
            }
            self.send_message_to_server(join_msg)
            
            # Start receiving messages
            self.start_receiving()
            
            # Switch to chat interface
            self.connection_frame.pack_forget()
            self.chat_frame.pack(fill=tk.BOTH, expand=True)
            
            # Update title
            self.root.title(f"Chat Application - {username}")
            
            # Focus on message entry
            self.message_entry.focus()
            
            messagebox.showinfo("Success", f"Connected as {username}")
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
    
    def start_local_server(self):
        """Start a local server."""
        def run_server():
            server = ChatServer()
            server.start_server()
        
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        
        messagebox.showinfo("Server Started", "Local server started on localhost:12345")
    
    def start_receiving(self):
        """Start receiving messages from server."""
        def receive_messages():
            while self.connected:
                try:
                    data = self.socket.recv(4096).decode('utf-8')
                    if not data:
                        break
                    
                    message = json.loads(data)
                    self.handle_received_message(message)
                    
                except ConnectionResetError:
                    break
                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    print(f"Receive error: {e}")
                    break
        
        receive_thread = threading.Thread(target=receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
    
    def handle_received_message(self, message):
        """Handle messages received from server."""
        msg_type = message.get('type')
        
        if msg_type in ['message', 'system', 'private', 'file']:
            self.display_message(message)
        elif msg_type == 'user_list':
            self.update_user_list(message['users'])
    
    def display_message(self, message):
        """Display message in chat window."""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = datetime.datetime.fromisoformat(message['timestamp'])
        time_str = timestamp.strftime("%H:%M:%S")
        
        if message['type'] == 'system':
            self.chat_display.insert(tk.END, f"[{time_str}] *** {message['message']} ***\n", 'system')
        elif message['type'] == 'private':
            self.chat_display.insert(tk.END, f"[{time_str}] (Private from {message['from']}): {message['message']}\n", 'private')
        elif message['type'] == 'file':
            self.chat_display.insert(tk.END, f"[{time_str}] {message['username']} shared file: {message['filename']}\n", 'file')
        else:
            self.chat_display.insert(tk.END, f"[{time_str}] {message['username']}: {message['message']}\n")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_message(self, event=None):
        """Send message to server."""
        message_text = self.message_entry.get().strip()
        if not message_text:
            return
        
        message = {
            'type': 'message',
            'username': self.username,
            'message': message_text,
            'room': self.current_room
        }
        
        self.send_message_to_server(message)
        self.message_entry.delete(0, tk.END)
    
    def send_message_to_server(self, message):
        """Send message to server."""
        try:
            data = json.dumps(message).encode('utf-8')
            self.socket.send(data)
        except Exception as e:
            messagebox.showerror("Send Error", f"Failed to send message: {e}")
    
    def insert_emoji(self, emoji):
        """Insert emoji into message entry."""
        current_text = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        self.message_entry.insert(0, current_text + emoji)
        self.message_entry.focus()
    
    def private_message(self):
        """Send private message to selected user."""
        selection = self.users_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user first")
            return
        
        target_user = self.users_listbox.get(selection[0])
        if target_user == self.username:
            messagebox.showwarning("Warning", "Cannot send private message to yourself")
            return
        
        message_text = simpledialog.askstring("Private Message", f"Message to {target_user}:")
        if message_text:
            private_msg = {
                'type': 'private',
                'from': self.username,
                'to': target_user,
                'message': message_text
            }
            self.send_message_to_server(private_msg)
    
    def change_room(self):
        """Change chat room."""
        new_room = simpledialog.askstring("Change Room", "Enter room name:")
        if new_room and new_room != self.current_room:
            room_change_msg = {
                'type': 'room_change',
                'username': self.username,
                'old_room': self.current_room,
                'new_room': new_room
            }
            self.send_message_to_server(room_change_msg)
            
            self.current_room = new_room
            self.room_label.config(text=f"Room: {new_room}")
    
    def request_user_list(self):
        """Request list of online users."""
        user_list_msg = {
            'type': 'user_list',
            'username': self.username
        }
        self.send_message_to_server(user_list_msg)
    
    def update_user_list(self, users):
        """Update the users listbox."""
        self.users_listbox.delete(0, tk.END)
        for user in users:
            self.users_listbox.insert(tk.END, user)
    
    def on_user_double_click(self, event):
        """Handle double-click on user list."""
        self.private_message()
    
    def share_file(self):
        """Share a file with the chat."""
        file_path = filedialog.askopenfilename(
            title="Select file to share",
            filetypes=[("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Read file and encode in base64
                with open(file_path, 'rb') as f:
                    file_data = base64.b64encode(f.read()).decode('utf-8')
                
                filename = os.path.basename(file_path)
                
                file_msg = {
                    'type': 'file',
                    'username': self.username,
                    'filename': filename,
                    'filedata': file_data,
                    'room': self.current_room
                }
                
                self.send_message_to_server(file_msg)
                
            except Exception as e:
                messagebox.showerror("File Error", f"Failed to share file: {e}")
    
    def on_closing(self):
        """Handle application closing."""
        if self.connected:
            self.connected = False
            if self.socket:
                self.socket.close()
        self.root.destroy()
    
    def run(self):
        """Run the chat client application."""
        self.root.mainloop()


def main():
    """Main function to run the chat application."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--server':
        # Run as server only
        print("🚀 Starting chat server...")
        server = ChatServer()
        try:
            server.start_server()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
    else:
        # Run as client
        client = ChatClient()
        client.run()


if __name__ == "__main__":
    main()
