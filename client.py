import socket
import threading
import time
import os
from tkinter import *

import chat_updater

GIST_IDS = chat_updater.GIST_IDS

os.system("cls")

if not chat_updater.is_client_updated():
    print("This client version is out of date!\n")

    print("You can get the most recent version by visiting the following link:")
    print(f"https://gist.github.com/Niveh/{GIST_IDS['client_script']}\n")

    print("Alternatively, I can update myself.")
    self_update_prompt = input(
        "Type 'yes' to update or anything else to exit: ").strip().lower()

    if self_update_prompt == "yes":
        chat_updater.self_update_client()

    exit()

elif not chat_updater.is_updater_updated():
    print("The chat_updater module is out of date!\n")

    print("You can get the most recent version by visiting the following link:")
    print(f"https://gist.github.com/Niveh/{GIST_IDS['chat_updater_script']}\n")

    print("Alternatively, I can update the module for you.")
    self_update_prompt = input(
        "Type 'yes' to update or anything else to exit: ").strip().lower()

    if self_update_prompt == "yes":
        chat_updater.self_update_updater()

    exit()

# GUI
WIDTH = 800
HEIGHT = 700

root = Tk()
root.title("Chat Room")
root.geometry(f"{WIDTH}x{HEIGHT}")
root.withdraw()

BG_GRAY = "#ABB2B9"
BG_COLOR = "#000000"
TEXT_COLOR = "#FFFFFF"

FONT = "Ubuntu 14"
FONT_BOLD = "Ubuntu 14 bold"

txt = Text(root, bg=BG_COLOR, fg=TEXT_COLOR, font=FONT, width=60)
txt.pack(expand=YES, fill=BOTH)
txt.config(state=DISABLED)

type_box = Entry(root, bg="#212121", fg=TEXT_COLOR, font=FONT, width=60)
type_box.pack(expand=NO, fill=BOTH)

SERVER, PORT = chat_updater.get_addr_from_gist()

ADDR = (SERVER, PORT)
FORMAT = "utf-8"
LEAVE_MESSAGE = "!leave"

stop_threads = False
message = ""
leave = False


def check_valid(letter):
    return letter.isalpha() or letter.isnumeric()


def set_nickname():
    nickname = input("Enter your nickname: ").replace(" ", "").strip().lower()
    if len(nickname) < 2 or len(nickname) > 20:
        print("Nickname must be between 2 and 20 characters!")
        set_nickname()

    elif len(set(nickname)) < 2:
        print("Invalid nickname!")
        set_nickname()

    elif list(filter(check_valid, list(nickname))) != list(nickname):
        print("Nickname cannot contain special characters!")
        set_nickname()
    else:
        return nickname


nickname = set_nickname()
root.deiconify()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def receive():
    while True:
        global stop_threads
        if stop_threads:
            break
        try:
            msg = client.recv(1024).decode(FORMAT).strip()
            if msg == "!NICKNAME":
                send(client, nickname)
            else:
                incoming_message_update_gui(msg)

        except:
            print("Connection lost.")
            client.close()
            break


def write():
    while True:
        global message
        if message:
            if message == LEAVE_MESSAGE:
                incoming_message_update_gui(LEAVE_MESSAGE)
                break

            send(client, message)
            message = ""

    send(client, LEAVE_MESSAGE)
    global stop_threads
    stop_threads = True
    receive_thread.join()

    time.sleep(2)
    root.withdraw()
    global leave
    leave = True
    exit()


def send(client, msg):
    message = msg.encode(FORMAT)
    client.send(message)


def insert_msg(txt, msg):
    txt.config(state=NORMAL)
    txt.insert(END, "\n" + msg)
    txt.config(state=DISABLED)
    txt.see(END)


def incoming_message_update_gui(msg):
    insert_msg(txt, msg)

    if msg == LEAVE_MESSAGE:
        insert_msg(txt, "Leaving channel...")

    # user = type_box.get().lower()

    # if (user == "!clear"):
    #     clear(txt)


def send_message_gui():
    msg = str(type_box.get())

    if len(msg) < 1:
        return

    MAX_LEN = 150
    if len(msg) > MAX_LEN:
        msg = msg[:MAX_LEN]

    global message
    message = msg

    # insert_msg(txt, msg)

    # user = type_box.get().lower()

    # if (user == "!clear"):
    #     clear(txt)

    type_box.delete(0, END)


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()


send_button = Button(root, text="Send", font=FONT_BOLD,
                     bg=BG_GRAY, command=send_message_gui)


def send_msg(event):
    send_button.invoke()


root.bind("<Return>", send_msg)
root.resizable(False, False)
root.mainloop()

if leave:
    exit()
