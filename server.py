import socket
import threading
import chat_updater
import time

SERVER = "localhost"
PORT = 999
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
LEAVE_MESSAGE = "!leave"
CHANNEL_NAME = "#chat-room"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = set()
clients_lock = threading.Lock()
nicknames = {}


def handle_client(conn, addr):
    print(f"New connection: {addr} connected.")

    try:
        connected = True
        while connected:
            if str(addr) not in nicknames:
                conn.send("!NICKNAME".encode(FORMAT))
                nicknames[str(addr)] = conn.recv(1024).decode(FORMAT)
                with clients_lock:
                    for client in clients:
                        client.sendall(
                            f"[{nicknames[str(addr)]}] has joined {CHANNEL_NAME}".encode(FORMAT))

            msg = conn.recv(1024).decode(FORMAT)
            if not msg:
                break

            if msg == LEAVE_MESSAGE:
                connected = False

            print(f"{nicknames[str(addr)]}: {msg}")
            with clients_lock:
                for client in clients:
                    client.sendall(
                        f"<{nicknames[str(addr)]}>  {msg}".encode(FORMAT))

    except socket.error as e:
        with clients_lock:
            clients.remove(conn)
            for client in clients:
                client.sendall(
                    f"\n[{nicknames[str(addr)]}] has left {CHANNEL_NAME}".encode(FORMAT))

            print(f"{nicknames[str(addr)]} left the chat.")
            nicknames.pop(str(addr), None)

        conn.close()

    finally:
        with clients_lock:
            for client in clients:
                client.sendall(
                    f"\n[{nicknames[str(addr)]}] has left {CHANNEL_NAME}".encode(FORMAT))

            print(f"{nicknames[str(addr)]} left the chat.")
            nicknames.pop(str(addr), None)
            clients.remove(conn)

        conn.close()


def start():
    print(f"Starting server!")
    time.sleep(1)

    print("Getting public IP...")
    PUBLIC_IP, PUBLIC_PORT = chat_updater.get_public_address()
    time.sleep(2)

    addr_gist = chat_updater.get_addr_from_gist()
    while addr_gist != (PUBLIC_IP, PUBLIC_PORT):
        print("Public IP is out of date!")
        print("Attemping to update the public IP data...")
        chat_updater.update_latest_addr_gist()
        time.sleep(5)
        addr_gist = chat_updater.get_addr_from_gist()

    print("IP succesfully updated!")
    print(f"Public IP: {PUBLIC_IP}, Port {PUBLIC_PORT}")

    server.listen()
    while True:
        conn, addr = server.accept()

        with clients_lock:
            clients.add(conn)

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


start()
