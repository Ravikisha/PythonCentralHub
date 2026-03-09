"""
Real-time Chat Application (WebSocket)

A Python application that enables real-time communication between clients using WebSocket.
Features include:
- Real-time messaging between multiple clients.
- Server-side implementation using `websockets` library.
- Client-side implementation for sending and receiving messages.
"""

import asyncio
import websockets

connected_clients = set()

async def handle_client(websocket, path):
    """Handle incoming messages from clients and broadcast them."""
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            await broadcast(message)
    except websockets.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected_clients.remove(websocket)

async def broadcast(message):
    """Send a message to all connected clients."""
    if connected_clients:  # Ensure there are clients to broadcast to
        await asyncio.wait([client.send(message) for client in connected_clients])

async def main():
    """Start the WebSocket server."""
    server = await websockets.serve(handle_client, "localhost", 8765)
    print("Server started on ws://localhost:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
