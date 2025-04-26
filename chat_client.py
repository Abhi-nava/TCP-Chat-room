import socket
import threading
import os
import time

class Client:
    def __init__(self, host='192.168.0.19', port=5555):
        self.host = host
        self.port = port
        self.nickname = ""
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receiving_file = False
        self.current_file = None
        self.file_name = ""
        self.file_size = 0
        self.bytes_received = 0
        self.sending_file = False
        self.last_sent_file = ""
    
    def connect(self):
        try:
            self.client.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def handle_file_receive(self, sock, filename, filesize):
        # Create downloads directory if it doesn't exist
        os.makedirs('downloads', exist_ok=True)
        
        download_path = os.path.join('downloads', filename)
        received_bytes = 0
        
        with open(download_path, 'wb') as f:
            while received_bytes < filesize:
                data = sock.recv(1024)
                if not data:
                    break
                f.write(data)
                received_bytes += len(data)
        
        print(f"File received and saved to {download_path}")

    def receive_messages(self):
        while True:
            try:
                data = self.client.recv(4096)
                if not data:
                    print("Connection to server lost")
                    if self.current_file:
                        self.current_file.close()
                    break
                
                # Check if this is a text control message or binary file data
                try:
                    # Try to decode as UTF-8, which would work for control messages
                    message = data.decode('utf-8')
                    
                    # Process control message
                    if message == "NICK":
                        self.client.send(self.nickname.encode('utf-8'))
                    
                    elif message.startswith("FILE_INCOMING:"):
                        # Format: FILE_INCOMING:filename:filesize:sender
                        parts = message.split(':')
                        self.file_name = parts[1]
                        self.file_size = int(parts[2])
                        sender = parts[3]
                        
                        # Check if this is a file we just sent
                        if sender == self.nickname and self.file_name == self.last_sent_file:
                            print(f"\nYour file '{self.file_name}' is being distributed to other clients")
                            # Skip receiving our own file
                            self.receiving_file = False
                        else:
                            print(f"\nReceiving file '{self.file_name}' from {sender} ({self.file_size} bytes)")
                            
                            # Send acknowledgment
                            self.client.send("READY".encode())
                            
                            # Handle the file receive
                            self.handle_file_receive(self.client, self.file_name, self.file_size)
                            self.receiving_file = False
                            self.current_file = None
                    
                    elif message.startswith("FILE_TRANSFER_COMPLETE:"):
                        parts = message.split(':')
                        completed_file = parts[1]
                        
                        # Only process if we're receiving this file
                        if self.receiving_file and completed_file == self.file_name and self.current_file:
                            self.current_file.flush()
                            self.current_file.close()
                            print(f"\nFile received and saved to downloads/{self.file_name}")
                            self.receiving_file = False
                            self.current_file = None
                        elif completed_file == self.last_sent_file:
                            print(f"\nYour file '{completed_file}' was successfully sent to all clients")
                            self.sending_file = False
                            self.last_sent_file = ""
                    
                    else:
                        # Regular text message
                        print(message)
                
                except UnicodeDecodeError:
                    # This is binary data, likely file content
                    if self.receiving_file and self.current_file:
                        self.current_file.write(data)
                        self.bytes_received += len(data)
                        
                        # Print progress
                        progress = (self.bytes_received / self.file_size) * 100
                        print(f"\rReceiving: {progress:.1f}% complete", end="")
                    else:
                        # Unexpected binary data - ignore
                        pass
            
            except Exception as e:
                print(f"Error in receive_messages: {e}")
                if self.current_file:
                    self.current_file.close()
                break
    
    def send_file(self, file_path):
        try:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return False
            
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            self.sending_file = True
            self.last_sent_file = file_name
            
            self.client.send(f"FILE_TRANSFER:{file_name}:{file_size}".encode('utf-8'))
            time.sleep(0.5)
            
            with open(file_path, 'rb') as file:
                bytes_sent = 0
                chunk_size = 4096
                
                while bytes_sent < file_size:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    
                    self.client.send(chunk)
                    bytes_sent += len(chunk)
                    
                    # Update progress on same line
                    progress = (bytes_sent / file_size) * 100
                    print(f"\rSending: {progress:.1f}% complete", end='', flush=True)
                
                # Print newline after transfer completes
                print("\nFile uploaded to server, distributing to clients...")
                return True
            
        except Exception as e:
            print(f"\nError sending file: {e}")
            self.sending_file = False
            self.last_sent_file = ""
            return False
    
    def send_message(self, message):
        try:
            self.client.send(message.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def start(self):
        print("=== Chat Client ===")
        self.nickname = input("Enter your nickname: ")
        
        if not self.connect():
            print("Failed to connect to server.")
            return
        
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        print("Connected to the server! Type 'file:path/to/file' to send a file.")
        
        while True:
            try:
                message = input()
                
                if message.lower() == 'quit':
                    break
                
                elif message.startswith('file:'):
                    file_path = message[5:].strip()
                    self.send_file(file_path)
                
                else:
                    self.send_message(message)
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                break
        
        print("Disconnecting from server...")
        if self.current_file:
            self.current_file.close()
        self.client.close()

if __name__ == "__main__":
    client = Client()
    client.start()