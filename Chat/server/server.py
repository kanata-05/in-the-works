import socket
import threading

clients = {}

def handle_client(conn):
    try:
        username = conn.recv(1024).decode().strip()
        if not username:
            conn.close()
            return
        clients[username] = conn
        print(f"{username} connected.")
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            if data.startswith("FRIEND_REQ:"):
                parts = data.split(":", 2)
                if len(parts) < 3:
                    continue
                sender, recipient = parts[1], parts[2]
                if recipient in clients:
                    try:
                        clients[recipient].sendall(f"FRIEND_REQ:{sender}".encode())
                    except Exception as e:
                        print(f"Error forwarding friend request to {recipient}: {e}")
                else:
                    conn.sendall(f"ERROR:User {recipient} not online".encode())
                continue
            if data.startswith("FRIEND_RESP:"):
                parts = data.split(":", 2)
                if len(parts) < 3:
                    continue
                original_requester, response = parts[1], parts[2]
                if original_requester in clients:
                    try:
                        clients[original_requester].sendall(f"FRIEND_RESP:{username}:{response}".encode())
                    except Exception as e:
                        print(f"Error sending friend response to {original_requester}: {e}")
                continue
            if data.startswith("BROADCAST:"):
                message = data[len("BROADCAST:"):].strip()
                sender = username
                for user, client_conn in clients.items():
                    if user != sender:
                        try:
                            client_conn.sendall(f"BROADCAST:{sender}:{message}".encode())
                        except Exception as e:
                            print(f"Error sending broadcast message to {user}: {e}")
                continue
            if data.startswith("MSG:"):
                parts = data.split(":", 2)
                if len(parts) < 3:
                    continue
                recipient, message = parts[1], parts[2]
                sender = username
                if recipient in clients:
                    try:
                        clients[recipient].sendall(f"FROM:{sender}:{message}".encode())
                    except Exception as e:
                        print(f"Error sending message to {recipient}: {e}")
                else:
                    conn.sendall(f"ERROR:User {recipient} not online".encode())
    except Exception as e:
        print("Client connection error:", e)
    finally:
        print(f"{username} disconnected.")
        if username in clients:
            del clients[username]
        conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 6168))
    server.listen()
    print("Server listening on port 6168...")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

if __name__ == '__main__':
    main()
