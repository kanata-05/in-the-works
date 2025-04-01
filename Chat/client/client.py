import socket
import threading
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ChatClient(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x500")
        self.resizable(False, False)
        try:
            self.iconbitmap("chat_icon.ico")
        except Exception as e:
            print("Icon not found, skipping icon setup.")
        self.username = ctk.CTkInputDialog(text="Enter your username", title="Username").get_input()
        if not self.username:
            self.username = "Anonymous"
        self.title(f"{self.username} - Chat")
        server_ip_input = ctk.CTkInputDialog(text="Enter server IP", title="Server IP").get_input()
        if not server_ip_input:
            server_ip_input = "127.0.0.1"
        self.server_ip = server_ip_input
        port_input = ctk.CTkInputDialog(text="Enter port", title="Port").get_input()
        self.server_port = int(port_input)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            self.client_socket.sendall(self.username.encode())
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.destroy()
            return
        self.server_ip_label = ctk.CTkLabel(self, text=f"Connected to: {self.server_ip}", anchor="e", font=("Helvetica", 10))
        self.server_ip_label.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
        self.left_frame = ctk.CTkFrame(self, width=200, corner_radius=15)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.friend_label = ctk.CTkLabel(self.left_frame, text="Friends", font=("Helvetica", 16))
        self.friend_label.pack(pady=(10, 5))
        self.friend_listbox = tk.Listbox(self.left_frame, height=15, bg="#2B2B2B", fg="white", selectbackground="#1C6EA4", selectforeground="white", bd=0, highlightthickness=0)
        self.friend_listbox.pack(padx=10, pady=5, fill="both", expand=True)
        self.friend_listbox.bind("<<ListboxSelect>>", self.select_friend)
        self.friend_listbox.insert("end", "Lounge")
        self.messages = {"Lounge": []}
        self.current_friend = "Lounge"
        self.add_friend_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Friend username...")
        self.add_friend_entry.pack(padx=10, pady=(5, 2))
        self.add_friend_button = ctk.CTkButton(self.left_frame, text="Send Friend Request", command=self.send_friend_request)
        self.add_friend_button.pack(padx=10, pady=(2, 10))
        self.right_frame = ctk.CTkFrame(self, corner_radius=15)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.chat_label = ctk.CTkLabel(self.right_frame, text="Chat", font=("Helvetica", 16))
        self.chat_label.pack(pady=(10, 5))
        self.chat_text = ctk.CTkTextbox(self.right_frame, height=15, corner_radius=10)
        self.chat_text.pack(padx=10, pady=5, fill="both", expand=True)
        self.chat_text.configure(state="disabled")
        self.entry_frame = ctk.CTkFrame(self.right_frame, corner_radius=15)
        self.entry_frame.pack(padx=10, pady=5, fill="x")
        self.message_entry = ctk.CTkEntry(self.entry_frame, placeholder_text="Type your message here...")
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        self.send_button = ctk.CTkButton(self.entry_frame, text="Send", command=self.send_message)
        self.send_button.pack(side="right", padx=(5, 10), pady=10)
        self.running = True
        threading.Thread(target=self.receive_messages, daemon=True).start()
    def select_friend(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            friend = event.widget.get(index)
            self.current_friend = friend
            self.load_chat(friend)
    def load_chat(self, friend):
        self.chat_text.configure(state="normal")
        self.chat_text.delete("1.0", "end")
        if friend in self.messages:
            for msg in self.messages[friend]:
                self.chat_text.insert("end", msg + "\n")
        self.chat_text.configure(state="disabled")
    def send_friend_request(self):
        friend_username = self.add_friend_entry.get().strip()
        if not friend_username:
            return
        if friend_username == self.username:
            messagebox.showerror("Error", "You cannot add yourself as a friend.")
            self.add_friend_entry.delete(0, "end")
            return
        try:
            self.client_socket.sendall(f"FRIEND_REQ:{self.username}:{friend_username}".encode())
            messagebox.showinfo("Friend Request", f"Friend request sent to {friend_username}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send friend request: {e}")
        self.add_friend_entry.delete(0, "end")
    def send_message(self):
        message = self.message_entry.get().strip()
        if not message:
            return
        if self.current_friend == "Lounge":
            try:
                data = f"BROADCAST:{message}"
                self.client_socket.sendall(data.encode())
                self.messages["Lounge"].append(f"You: {message}")
                self.load_chat("Lounge")
                self.message_entry.delete(0, "end")
            except Exception as e:
                messagebox.showerror("Erm", f"Err: {e}")
    def receive_messages(self):
        while self.running:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    continue
            except Exception as e:
                print("Err:", e)
                self.running = False
                break
    def on_closing(self):
        self.running = False
        self.client_socket.close()
        self.destroy()
if __name__ == "__main__":
    app = ChatClient()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
