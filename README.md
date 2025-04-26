# Chat Application with File Sharing

A simple Python-based chat application that allows multiple users to communicate in real-time and share files. The application consists of a server component and client components (command-line and GUI interfaces).

## Features

- Real-time text messaging between multiple clients
- File sharing capabilities (send and receive files)
- Progress tracking for file transfers
- Command line and GUI interfaces for clients
- User nicknames for identification

## Components

The application consists of three main Python files:

1. **chat_server.py** - The server component that manages connections and message/file distribution
2. **chat_client.py** - Command-line client interface
3. **gui.py** - Graphical user interface for the client

## Requirements

- Python 3.6 or higher
- Standard library modules (no external dependencies):
  - socket
  - threading
  - tkinter (for GUI)
  - os
  - time

## Usage

### Running the Server

Start the server before launching any clients:

```bash
python chat_server.py
```

By default, the server listens on all interfaces (0.0.0.0) on port 5555. You can modify these settings in the `__init__` method of the `Server` class.

### Running the Command-Line Client

```bash
python chat_client.py
```

The command-line client will prompt you to enter a nickname. After connecting, you can:
- Send text messages by typing and pressing Enter
- Send files with the command `file:/path/to/file`
- Quit the application by typing `quit`

### Running the GUI Client

```bash
python gui.py
```

The GUI provides a more user-friendly interface with:
- A text area displaying chat messages
- An input field for typing messages
- Buttons for sending messages and files
- Progress tracking for file transfers

## File Transfer

Files sent by users are:
1. Uploaded to the server
2. Distributed to all connected clients
3. Saved in a `downloads` folder in the client's directory

The application supports files of any type and shows transfer progress in real-time.

## Network Protocol

The application uses a simple text-based protocol for control messages:
- `NICK` - Request for client nickname
- `FILE_TRANSFER:filename:filesize` - Initiates a file transfer
- `FILE_INCOMING:filename:filesize:sender` - Notifies clients about incoming file
- `FILE_TRANSFER_COMPLETE:filename` - Signals completion of file transfer

Binary data is sent directly without encoding for file transfers.

## Customization

You can customize the server address and port by modifying the default values in the client classes:

```python
# In chat_client.py or gui.py
client = Client(host='your_server_ip', port=your_port)
```

## Limitations

- No encryption for messages or file transfers
- No authentication beyond nicknames
- No persistent storage of messages
- All clients receive all messages and files

## Future Improvements

- End-to-end encryption for messages and files
- Private messaging between users
- User authentication
- Message history storage
- File transfer resume capability
- Custom avatars and rich text formatting