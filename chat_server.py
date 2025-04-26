import socket
import threading
import os
import time
import struct

class Server:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        self.clients = []
        self.nicknames = []
        self.file_transfers = {}  # Track active file transfers
        
        print(f"Server started on {self.host}:{self.port}")
        
    def broadcast(self, message, sender_socket=None):
        for client in self.clients:
            if client != sender_socket:  # Don't send back to sender
                try:
                    client.send(message)
                except:
                    self.remove_client(client)
    
    def broadcast_to_all(self, message):
        """Send to all clients including sender"""
        for client in self.clients:
            try:
                client.send(message)
            except:
                self.remove_client(client)
    
    def handle_file_transfer(self, client, file_name, file_size, sender_nickname):
        try:
            # Notify all clients about the incoming file
            file_notice = f"FILE_INCOMING:{file_name}:{file_size}:{sender_nickname}".encode('utf-8')
            self.broadcast_to_all(file_notice)
            time.sleep(0.5)  # Give clients time to prepare
            
            # Track this client as being in file transfer mode
            self.file_transfers[client] = {
                'file_name': file_name,
                'file_size': file_size,
                'bytes_received': 0
            }
            
            # Now let the main client handler receive the file data
            # We'll return here and let the main loop handle the actual data
        
        except Exception as e:
            print(f"Error setting up file transfer: {e}")
            if client in self.file_transfers:
                del self.file_transfers[client]
    
    def handle_client(self, client, nickname):
        while True:
            try:
                # Check if this client is currently transferring a file
                if client in self.file_transfers:
                    transfer_info = self.file_transfers[client]
                    remaining = transfer_info['file_size'] - transfer_info['bytes_received']
                    
                    if remaining <= 0:
                        # We've received all the expected data
                        del self.file_transfers[client]
                        continue
                    
                    # Receive file chunk (binary data)
                    chunk_size = min(4096, remaining)
                    chunk = client.recv(chunk_size)
                    
                    if not chunk:
                        print(f"Connection lost during file transfer from {nickname}")
                        del self.file_transfers[client]
                        break
                    
                    # Update bytes received
                    transfer_info['bytes_received'] += len(chunk)
                    
                    # Forward chunk to all other clients without processing
                    self.broadcast(chunk, client)
                    
                    # Show progress
                    progress = (transfer_info['bytes_received'] / transfer_info['file_size']) * 100
                    print(f"\rFile transfer progress: {progress:.1f}%", end="")
                    
                    # Check if transfer is complete
                    if transfer_info['bytes_received'] >= transfer_info['file_size']:
                        print(f"\nFile transfer complete: {transfer_info['file_name']} ({transfer_info['file_size']} bytes)")
                        complete_notice = f"FILE_TRANSFER_COMPLETE:{transfer_info['file_name']}".encode('utf-8')
                        self.broadcast_to_all(complete_notice)
                        del self.file_transfers[client]
                
                else:
                    # Normal message handling mode
                    message = client.recv(4096)
                    
                    if not message:
                        break
                    
                    if message.startswith(b'FILE_TRANSFER:'):
                        # Parse file info: FILE_TRANSFER:filename:filesize
                        parts = message.decode('utf-8').split(':')
                        file_name = parts[1]
                        file_size = int(parts[2])
                        
                        print(f"File transfer initiated by {nickname}: {file_name} ({file_size} bytes)")
                        
                        # Set up the file transfer
                        self.handle_file_transfer(client, file_name, file_size, nickname)
                    
                    else:
                        # Regular chat message, broadcast to all
                        try:
                            msg_with_nickname = f"{nickname}: {message.decode('utf-8')}"
                            print(msg_with_nickname)
                            self.broadcast(msg_with_nickname.encode('utf-8'), client)
                        except UnicodeDecodeError:
                            # This might be binary data that's not properly framed as a file transfer
                            print(f"Received binary data outside file transfer mode from {nickname}")
                            # Just ignore it
            
            except Exception as e:
                print(f"Error handling client {nickname}: {e}")
                if client in self.file_transfers:
                    del self.file_transfers[client]
                self.remove_client(client)
                break
    
    def remove_client(self, client):
        if client in self.clients:
            index = self.clients.index(client)
            nickname = self.nicknames[index]
            self.broadcast(f"{nickname} left the chat!".encode('utf-8'))
            self.clients.remove(client)
            self.nicknames.pop(index)
            if client in self.file_transfers:
                del self.file_transfers[client]
            client.close()
    
    def receive(self):
        while True:
            try:
                client, address = self.server.accept()
                print(f"Connected with {address}")
                
                client.send("NICK".encode('utf-8'))
                nickname = client.recv(1024).decode('utf-8')
                
                self.nicknames.append(nickname)
                self.clients.append(client)
                
                print(f"Nickname of the client is {nickname}")
                self.broadcast(f"{nickname} joined the chat!".encode('utf-8'))
                client.send("Connected to the server!".encode('utf-8'))
                
                thread = threading.Thread(target=self.handle_client, args=(client, nickname))
                thread.daemon = True
                thread.start()
            
            except Exception as e:
                print(f"Error in receive: {e}")
                break

if __name__ == "__main__":
    server = Server()
    server.receive()