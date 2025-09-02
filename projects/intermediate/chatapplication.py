# Chat Application with Socket Programming

import socket
import threading
import json
import time
import hashlib
import datetime
from typing import Dict, List, Optional, Tuple
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import queue
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChatMessage:
    """Represents a chat message"""
    def __init__(self, username: str, content: str, message_type: str = "message", 
                 timestamp: Optional[datetime.datetime] = None):
        self.username = username
        self.content = content
        self.message_type = message_type  # message, join, leave, system
        self.timestamp = timestamp or datetime.datetime.now()
        self.id = hashlib.md5(f"{username}{content}{self.timestamp}".encode()).hexdigest()[:8]
    
    def to_dict(self) -> dict:
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'content': self.content,
            'type': self.message_type,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ChatMessage':
        """Create message from dictionary"""
        timestamp = datetime.datetime.fromisoformat(data['timestamp'])
        msg = cls(data['username'], data['content'], data['type'], timestamp)
        msg.id = data['id']
        return msg

class ChatServer:
    """Chat server handling multiple clients"""
    
    def __init__(self, host: str = 'localhost', port: int = 12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.clients: Dict[socket.socket, dict] = {}
        self.message_history: List[ChatMessage] = []
        self.running = False
        self.max_history = 100
        
        # Room management
        self.rooms: Dict[str, List[socket.socket]] = {'general': []}
        self.default_room = 'general'
    
    def start(self):
        """Start the chat server"""
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            logger.info(f"Chat server started on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, address = self.socket.accept()
                    logger.info(f"New connection from {address}")
                    
                    # Start client handler thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except OSError:
                    if self.running:
                        logger.error("Error accepting connections")
                    break
                    
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket: socket.socket, address: Tuple[str, int]):
        """Handle individual client connection"""
        username = None
        
        try:
            # Initial handshake - get username
            client_socket.send(json.dumps({
                'type': 'handshake',
                'message': 'Please provide username'
            }).encode('utf-8'))
            
            # Receive username
            data = client_socket.recv(1024).decode('utf-8')
            handshake_data = json.loads(data)
            username = handshake_data.get('username', f'User_{address[1]}')
            
            # Check if username is already taken
            while any(client['username'] == username for client in self.clients.values()):
                username = f"{username}_{len(self.clients)}"
            
            # Add client to clients list
            self.clients[client_socket] = {
                'username': username,
                'address': address,
                'room': self.default_room,
                'joined_at': datetime.datetime.now()
            }
            
            # Add to default room
            self.rooms[self.default_room].append(client_socket)
            
            # Send welcome message and recent history
            welcome_data = {
                'type': 'welcome',
                'username': username,
                'room': self.default_room,
                'history': [msg.to_dict() for msg in self.message_history[-20:]]
            }
            client_socket.send(json.dumps(welcome_data).encode('utf-8'))
            
            # Broadcast join message
            join_message = ChatMessage(username, f"{username} joined the chat", "join")
            self.broadcast_message(join_message, exclude=client_socket)
            self.add_to_history(join_message)
            
            # Handle client messages
            while self.running:
                try:
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                    
                    message_data = json.loads(data)
                    self.process_message(client_socket, message_data)
                    
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from {username}")
                except Exception as e:
                    logger.error(f"Error handling message from {username}: {e}")
                    break
        
        except Exception as e:
            logger.error(f"Error in client handler for {address}: {e}")
        
        finally:
            self.disconnect_client(client_socket, username)
    
    def process_message(self, client_socket: socket.socket, message_data: dict):
        """Process incoming message from client"""
        client_info = self.clients.get(client_socket)
        if not client_info:
            return
        
        username = client_info['username']
        message_type = message_data.get('type', 'message')
        content = message_data.get('content', '')
        
        if message_type == 'message':
            # Regular chat message
            if content.strip():
                chat_message = ChatMessage(username, content, "message")
                self.broadcast_message(chat_message, room=client_info['room'])
                self.add_to_history(chat_message)
        
        elif message_type == 'command':
            # Handle chat commands
            self.handle_command(client_socket, content)
        
        elif message_type == 'private':
            # Private message
            target_username = message_data.get('target')
            self.send_private_message(client_socket, target_username, content)
    
    def handle_command(self, client_socket: socket.socket, command: str):
        """Handle chat commands"""
        client_info = self.clients[client_socket]
        username = client_info['username']
        
        parts = command.strip().split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        
        if cmd == '/help':
            help_text = """
Available commands:
/help - Show this help
/users - List online users
/rooms - List available rooms
/join <room> - Join a room
/create <room> - Create a new room
/pm <username> <message> - Send private message
/time - Show current server time
"""
            self.send_system_message(client_socket, help_text)
        
        elif cmd == '/users':
            users = [info['username'] for info in self.clients.values()]
            user_list = f"Online users ({len(users)}): {', '.join(users)}"
            self.send_system_message(client_socket, user_list)
        
        elif cmd == '/rooms':
            room_info = []
            for room, clients in self.rooms.items():
                room_info.append(f"{room} ({len(clients)} users)")
            room_list = f"Available rooms: {', '.join(room_info)}"
            self.send_system_message(client_socket, room_list)
        
        elif cmd == '/join' and len(parts) > 1:
            new_room = parts[1]
            self.move_client_to_room(client_socket, new_room)
        
        elif cmd == '/create' and len(parts) > 1:
            new_room = parts[1]
            if new_room not in self.rooms:
                self.rooms[new_room] = []
                self.send_system_message(client_socket, f"Room '{new_room}' created")
                self.move_client_to_room(client_socket, new_room)
            else:
                self.send_system_message(client_socket, f"Room '{new_room}' already exists")
        
        elif cmd == '/pm' and len(parts) > 2:
            target_username = parts[1]
            message_content = ' '.join(parts[2:])
            self.send_private_message(client_socket, target_username, message_content)
        
        elif cmd == '/time':
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.send_system_message(client_socket, f"Server time: {current_time}")
        
        else:
            self.send_system_message(client_socket, "Unknown command. Type /help for available commands.")
    
    def move_client_to_room(self, client_socket: socket.socket, room_name: str):
        """Move client to a different room"""
        client_info = self.clients[client_socket]
        username = client_info['username']
        old_room = client_info['room']
        
        # Remove from old room
        if client_socket in self.rooms[old_room]:
            self.rooms[old_room].remove(client_socket)
        
        # Add to new room
        if room_name not in self.rooms:
            self.rooms[room_name] = []
        
        self.rooms[room_name].append(client_socket)
        client_info['room'] = room_name
        
        # Notify client
        self.send_system_message(client_socket, f"Moved to room '{room_name}'")
        
        # Notify rooms
        leave_msg = ChatMessage(username, f"{username} left the room", "leave")
        self.broadcast_message(leave_msg, room=old_room, exclude=client_socket)
        
        join_msg = ChatMessage(username, f"{username} joined the room", "join")
        self.broadcast_message(join_msg, room=room_name, exclude=client_socket)
    
    def send_private_message(self, sender_socket: socket.socket, target_username: str, content: str):
        """Send private message between users"""
        sender_info = self.clients[sender_socket]
        sender_username = sender_info['username']
        
        # Find target client
        target_socket = None
        for client_socket, info in self.clients.items():
            if info['username'] == target_username:
                target_socket = client_socket
                break
        
        if target_socket:
            # Send to target
            pm_data = {
                'type': 'private',
                'from': sender_username,
                'content': content,
                'timestamp': datetime.datetime.now().isoformat()
            }
            target_socket.send(json.dumps(pm_data).encode('utf-8'))
            
            # Confirm to sender
            self.send_system_message(sender_socket, f"Private message sent to {target_username}")
        else:
            self.send_system_message(sender_socket, f"User '{target_username}' not found")
    
    def send_system_message(self, client_socket: socket.socket, content: str):
        """Send system message to specific client"""
        system_data = {
            'type': 'system',
            'content': content,
            'timestamp': datetime.datetime.now().isoformat()
        }
        try:
            client_socket.send(json.dumps(system_data).encode('utf-8'))
        except:
            pass
    
    def broadcast_message(self, message: ChatMessage, room: str = None, exclude: socket.socket = None):
        """Broadcast message to clients"""
        message_data = json.dumps(message.to_dict()).encode('utf-8')
        
        if room:
            # Broadcast to specific room
            clients_to_send = self.rooms.get(room, [])
        else:
            # Broadcast to all clients
            clients_to_send = list(self.clients.keys())
        
        for client_socket in clients_to_send[:]:  # Copy list to avoid modification during iteration
            if client_socket != exclude:
                try:
                    client_socket.send(message_data)
                except:
                    # Client disconnected, remove from lists
                    self.disconnect_client(client_socket)
    
    def add_to_history(self, message: ChatMessage):
        """Add message to history"""
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]
    
    def disconnect_client(self, client_socket: socket.socket, username: str = None):
        """Handle client disconnection"""
        if client_socket in self.clients:
            client_info = self.clients[client_socket]
            username = username or client_info['username']
            room = client_info['room']
            
            # Remove from room
            if room in self.rooms and client_socket in self.rooms[room]:
                self.rooms[room].remove(client_socket)
            
            # Remove from clients
            del self.clients[client_socket]
            
            # Broadcast leave message
            leave_message = ChatMessage(username, f"{username} left the chat", "leave")
            self.broadcast_message(leave_message, room=room, exclude=client_socket)
            self.add_to_history(leave_message)
            
            logger.info(f"Client {username} disconnected")
        
        try:
            client_socket.close()
        except:
            pass
    
    def stop(self):
        """Stop the server"""
        self.running = False
        
        # Close all client connections
        for client_socket in list(self.clients.keys()):
            try:
                client_socket.close()
            except:
                pass
        
        # Close server socket
        try:
            self.socket.close()
        except:
            pass
        
        logger.info("Chat server stopped")

class ChatClient:
    """Chat client for connecting to server"""
    
    def __init__(self, username: str, host: str = 'localhost', port: int = 12345):
        self.username = username
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.message_queue = queue.Queue()
        
    def connect(self) -> bool:
        """Connect to chat server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            # Wait for handshake
            data = self.socket.recv(1024).decode('utf-8')
            handshake = json.loads(data)
            
            if handshake['type'] == 'handshake':
                # Send username
                response = {'username': self.username}
                self.socket.send(json.dumps(response).encode('utf-8'))
                
                # Wait for welcome
                data = self.socket.recv(4096).decode('utf-8')
                welcome = json.loads(data)
                
                if welcome['type'] == 'welcome':
                    self.connected = True
                    self.username = welcome['username']  # May have been modified
                    
                    # Start message listener thread
                    listener_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
                    listener_thread.start()
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def listen_for_messages(self):
        """Listen for incoming messages"""
        while self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                message_data = json.loads(data)
                self.message_queue.put(message_data)
                
            except Exception as e:
                if self.connected:
                    logger.error(f"Error receiving message: {e}")
                break
        
        self.connected = False
    
    def send_message(self, content: str):
        """Send chat message"""
        if not self.connected:
            return False
        
        try:
            message_data = {
                'type': 'message',
                'content': content
            }
            self.socket.send(json.dumps(message_data).encode('utf-8'))
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def send_command(self, command: str):
        """Send chat command"""
        if not self.connected:
            return False
        
        try:
            command_data = {
                'type': 'command',
                'content': command
            }
            self.socket.send(json.dumps(command_data).encode('utf-8'))
            return True
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

class ChatGUI:
    """GUI for chat client"""
    
    def __init__(self):
        self.client = None
        self.root = tk.Tk()
        self.root.title("Chat Application")
        self.root.geometry("800x600")
        
        self.setup_ui()
        self.update_messages_thread = None
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Connection frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection", padding="5")
        conn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        conn_frame.columnconfigure(1, weight=1)
        
        # Connection controls
        ttk.Label(conn_frame, text="Username:").grid(row=0, column=0, sticky=tk.W)
        self.username_var = tk.StringVar(value="User")
        ttk.Entry(conn_frame, textvariable=self.username_var, width=15).grid(row=0, column=1, padx=(5, 10), sticky=tk.W)
        
        ttk.Label(conn_frame, text="Host:").grid(row=0, column=2, sticky=tk.W)
        self.host_var = tk.StringVar(value="localhost")
        ttk.Entry(conn_frame, textvariable=self.host_var, width=15).grid(row=0, column=3, padx=(5, 10), sticky=tk.W)
        
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=4, sticky=tk.W)
        self.port_var = tk.StringVar(value="12345")
        ttk.Entry(conn_frame, textvariable=self.port_var, width=8).grid(row=0, column=5, padx=(5, 10), sticky=tk.W)
        
        self.connect_button = ttk.Button(conn_frame, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=0, column=6, padx=(5, 0))
        
        self.disconnect_button = ttk.Button(conn_frame, text="Disconnect", command=self.disconnect_from_server, state=tk.DISABLED)
        self.disconnect_button.grid(row=0, column=7, padx=(5, 0))
        
        # Status
        self.status_var = tk.StringVar(value="Not connected")
        status_label = ttk.Label(conn_frame, textvariable=self.status_var, foreground="red")
        status_label.grid(row=1, column=0, columnspan=8, sticky=tk.W, pady=(5, 0))
        
        # Chat frame
        chat_frame = ttk.LabelFrame(main_frame, text="Chat", padding="5")
        chat_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Messages display
        self.messages_display = scrolledtext.ScrolledText(chat_frame, state=tk.DISABLED, height=20)
        self.messages_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Message input frame
        input_frame = ttk.Frame(chat_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        input_frame.columnconfigure(0, weight=1)
        
        # Message input
        self.message_var = tk.StringVar()
        self.message_entry = ttk.Entry(input_frame, textvariable=self.message_var)
        self.message_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.message_entry.bind('<Return>', self.send_message_event)
        
        # Send button
        self.send_button = ttk.Button(input_frame, text="Send", command=self.send_message, state=tk.DISABLED)
        self.send_button.grid(row=0, column=1)
        
        # Help text
        help_frame = ttk.Frame(main_frame)
        help_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        help_text = "Commands: /help, /users, /rooms, /join <room>, /create <room>, /pm <user> <msg>, /time"
        ttk.Label(help_frame, text=help_text, font=("TkDefaultFont", 8)).pack()
    
    def connect_to_server(self):
        """Connect to chat server"""
        username = self.username_var.get().strip()
        host = self.host_var.get().strip()
        
        try:
            port = int(self.port_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
            return
        
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        # Create client and connect
        self.client = ChatClient(username, host, port)
        
        if self.client.connect():
            self.status_var.set(f"Connected as {self.client.username}")
            self.status_var.set(f"Connected as {self.client.username}")
            
            # Update UI state
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.send_button.config(state=tk.NORMAL)
            self.message_entry.config(state=tk.NORMAL)
            
            # Start message update thread
            self.update_messages_thread = threading.Thread(target=self.update_messages, daemon=True)
            self.update_messages_thread.start()
            
            # Clear and focus message entry
            self.message_entry.focus()
            
        else:
            messagebox.showerror("Error", "Failed to connect to server")
            self.client = None
    
    def disconnect_from_server(self):
        """Disconnect from chat server"""
        if self.client:
            self.client.disconnect()
            self.client = None
        
        # Update UI state
        self.status_var.set("Not connected")
        self.connect_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        self.message_entry.config(state=tk.DISABLED)
    
    def send_message_event(self, event):
        """Handle Enter key press"""
        self.send_message()
    
    def send_message(self):
        """Send message or command"""
        if not self.client or not self.client.connected:
            return
        
        content = self.message_var.get().strip()
        if not content:
            return
        
        if content.startswith('/'):
            # Send as command
            self.client.send_command(content)
        else:
            # Send as message
            self.client.send_message(content)
        
        # Clear input
        self.message_var.set("")
    
    def update_messages(self):
        """Update messages from server"""
        while self.client and self.client.connected:
            try:
                # Get message from queue (blocking with timeout)
                message_data = self.client.message_queue.get(timeout=1.0)
                
                # Update UI in main thread
                self.root.after(0, self.display_message, message_data)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error updating messages: {e}")
                break
    
    def display_message(self, message_data: dict):
        """Display message in chat window"""
        self.messages_display.config(state=tk.NORMAL)
        
        message_type = message_data.get('type', 'message')
        
        if message_type == 'welcome':
            # Display welcome message and history
            username = message_data['username']
            room = message_data['room']
            self.messages_display.insert(tk.END, f"=== Welcome {username} to room '{room}' ===\n", 'system')
            
            # Display history
            history = message_data.get('history', [])
            for msg_dict in history:
                self.format_and_insert_message(msg_dict)
        
        elif message_type == 'system':
            # System message
            content = message_data['content']
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            self.messages_display.insert(tk.END, f"[{timestamp}] SYSTEM: {content}\n", 'system')
        
        elif message_type == 'private':
            # Private message
            from_user = message_data['from']
            content = message_data['content']
            timestamp = datetime.datetime.fromisoformat(message_data['timestamp']).strftime("%H:%M:%S")
            self.messages_display.insert(tk.END, f"[{timestamp}] PRIVATE from {from_user}: {content}\n", 'private')
        
        else:
            # Regular message
            self.format_and_insert_message(message_data)
        
        # Configure tags for styling
        self.messages_display.tag_config('system', foreground='blue')
        self.messages_display.tag_config('private', foreground='purple')
        self.messages_display.tag_config('join', foreground='green')
        self.messages_display.tag_config('leave', foreground='red')
        
        # Scroll to bottom
        self.messages_display.see(tk.END)
        self.messages_display.config(state=tk.DISABLED)
    
    def format_and_insert_message(self, message_data: dict):
        """Format and insert a chat message"""
        username = message_data['username']
        content = message_data['content']
        msg_type = message_data.get('type', 'message')
        timestamp = datetime.datetime.fromisoformat(message_data['timestamp']).strftime("%H:%M:%S")
        
        if msg_type == 'join':
            self.messages_display.insert(tk.END, f"[{timestamp}] {content}\n", 'join')
        elif msg_type == 'leave':
            self.messages_display.insert(tk.END, f"[{timestamp}] {content}\n", 'leave')
        else:
            self.messages_display.insert(tk.END, f"[{timestamp}] {username}: {content}\n")
    
    def run(self):
        """Run the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        if self.client:
            self.client.disconnect()
        self.root.destroy()

def start_server():
    """Start chat server"""
    print("Starting chat server...")
    server = ChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()

def start_client():
    """Start chat client GUI"""
    app = ChatGUI()
    app.run()

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'server':
            start_server()
        elif sys.argv[1] == 'client':
            start_client()
        else:
            print("Usage: python chatapp.py [server|client]")
    else:
        # Default to client
        start_client()

if __name__ == "__main__":
    main()
