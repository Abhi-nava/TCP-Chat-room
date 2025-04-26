import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
from chat_client import Client
import os

class ClientGUI:
    def __init__(self):
        self.client = Client()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Chat Application")
        self.root.geometry("600x800")
        
        # Create chat display area
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=70, height=30)
        self.chat_area.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
        self.chat_area.config(state='disabled')
        
        # Create message input field
        self.msg_entry = tk.Entry(self.root, width=50)
        self.msg_entry.grid(row=1, column=0, padx=10, pady=5)
        self.msg_entry.bind('<Return>', lambda e: self.send_message())
        
        # Create buttons
        self.send_btn = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_btn.grid(row=1, column=1, pady=5)
        
        self.file_btn = tk.Button(self.root, text="Send File", command=self.browse_file)
        self.file_btn.grid(row=1, column=2, pady=5, padx=5)
        
        # Progress bar for file transfers
        self.progress_label = tk.Label(self.root, text="")
        self.progress_label.grid(row=2, column=0, columnspan=3)
        
        # Override print function for GUI display
        self.original_print = print
        import builtins
        builtins.print = self.gui_print
        
        # Get nickname before starting
        self.get_nickname()
        
        # Set up close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_nickname(self):
        nickname_window = tk.Toplevel(self.root)
        nickname_window.title("Enter Nickname")
        nickname_window.geometry("300x150")
        
        tk.Label(nickname_window, text="Enter your nickname:").pack(pady=10)
        nickname_entry = tk.Entry(nickname_window, width=30)
        nickname_entry.pack(pady=5)
        
        def submit_nickname():
            nickname = nickname_entry.get().strip()
            if nickname:
                self.client.nickname = nickname
                nickname_window.destroy()
                self.connect_to_server()
            else:
                messagebox.showerror("Error", "Nickname cannot be empty!")
        
        tk.Button(nickname_window, text="Join Chat", command=submit_nickname).pack(pady=10)

    def connect_to_server(self):
        if self.client.connect():
            # Start message receiving thread
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.gui_print("Connected to server!")
        else:
            messagebox.showerror("Error", "Could not connect to server!")
            self.root.quit()

    def gui_print(self, *args, **kwargs):
        message = ' '.join(map(str, args))
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + '\n')
        self.chat_area.see(tk.END)
        self.chat_area.config(state='disabled')

    def update_progress(self, progress):
        self.root.after(0, lambda: self.progress_label.config(
            text=f"Transfer Progress: {progress:.1f}%"
        ))

    def send_message(self):
        message = self.msg_entry.get().strip()
        if message:
            if self.client.send_message(message):
                # Message sent successfully, display in GUI
                self.gui_print(f"You: {message}")
            self.msg_entry.delete(0, tk.END)

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.send_btn.config(state='disabled')
            self.file_btn.config(state='disabled')
            
            def file_transfer():
                try:
                    filename = os.path.basename(file_path)
                    self.gui_print(f"You: Sending file '{filename}'...")
                    # Monitor progress
                    original_print = print
                    def progress_print(*args, **kwargs):
                        if args and isinstance(args[0], str):
                            if args[0].startswith('\rSending:'):
                                progress = float(args[0].split('%')[0].split(':')[1])
                                self.update_progress(progress)
                            elif not args[0].startswith('You:'):  # Avoid duplicate "You:" messages
                                self.gui_print(*args, **kwargs)
                    
                    import builtins
                    builtins.print = progress_print
                    self.client.send_file(file_path)
                    builtins.print = original_print
                finally:
                    self.root.after(0, self.enable_buttons)
            
            threading.Thread(target=file_transfer, daemon=True).start()

    def enable_buttons(self):
        self.send_btn.config(state='normal')
        self.file_btn.config(state='normal')
        self.progress_label.config(text="")

    def receive_messages(self):
        while True:
            try:
                data = self.client.client.recv(4096)
                if not data:
                    self.gui_print("Disconnected from server")
                    break
                
                try:
                    # Try to decode as text message
                    message = data.decode('utf-8')
                    
                    if message == "NICK":
                        self.client.client.send(self.client.nickname.encode('utf-8'))
                    elif message.startswith("FILE_INCOMING:"):
                        parts = message.split(':')
                        filename = parts[1]
                        filesize = int(parts[2])
                        sender = parts[3]
                        
                        if sender != self.client.nickname:
                            self.gui_print(f"Receiving file '{filename}' from {sender}")
                            self.client.handle_file_receive(self.client.client, filename, filesize)
                            self.gui_print(f"File saved to downloads/{filename}")
                    else:
                        self.gui_print(message)
                        
                except UnicodeDecodeError:
                    # Binary data for file transfer
                    pass
                    
            except Exception as e:
                self.gui_print(f"Error: {e}")
                break

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            try:
                self.client.client.close()
            except:
                pass
            self.root.quit()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = ClientGUI()
    gui.run()
