# Chat Application with File Sharing

A Python-based chat application that allows users to communicate in real-time and share files over a network.

## Features

- Real-time text messaging between multiple clients
- File sharing capabilities with progress tracking
- Both command-line and graphical user interfaces
- User identification via nicknames
- Simple server setup and configuration

## Components

The application consists of three main Python files:

1. **chat_server.py** - Server component that manages connections and message/file distribution
2. **chat_client.py** - Command-line client interface
3. **gui.py** - Graphical user interface for the client

## Requirements

- Python 3.6+
- Standard library modules:
  - socket
  - threading
  - tkinter (for GUI)
  - os
  - time

## Usage

### Starting the Server

```bash
python chat_server.py
```

The server listens on all interfaces (0.0.0.0) on port 5555 by default.

### Using the Command-Line Client

```bash
python chat_client.py
```

After entering a nickname, you can:
- Send text messages by typing and pressing Enter
- Send files with the command `file:/path/to/file`
- Exit with the command `quit`

### Using the GUI Client

```bash
python gui.py
```

The GUI provides:
- A text area displaying chat messages
- An input field for typing messages
- Buttons for sending messages and files
- Progress tracking for file transfers

## File Transfer

Files are:
1. Uploaded to the server
2. Distributed to all connected clients
3. Saved in a `downloads` folder in each client's directory

## Configuration

You can customize the server address in the Client class:

```python
# In chat_client.py, change the default host and port
def __init__(self, host='your_server_ip', port=your_port):
```

## Limitations

- No encryption for messages or file transfers
- No authentication beyond nicknames
- No persistent storage of messages

## Future Improvements

- End-to-end encryption
- User authentication
- Private messaging
- Message history
- Support for larger files with resumable transfers